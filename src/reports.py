"""SQL reports calculated from actual records, plus shareable report artifacts."""
import json
import os
from pathlib import Path
import stat
import tempfile
from .connection_pool import ROOT, pooled_cursor

REPORT_QUERIES = {
    "summary": """SELECT COUNT(*) AS TotalOrders, COALESCE(SUM(TotalCost),0) AS TotalSales,
        COALESCE(ROUND(AVG(TotalCost),2),0) AS AverageOrderValue,
        COALESCE(MAX(TotalCost),0) AS HighestOrderValue,
        COALESCE(MIN(TotalCost),0) AS LowestOrderValue FROM Orders""",
    "category_sales": """SELECT m.Type, SUM(oi.Quantity) AS QuantitySold, SUM(oi.Quantity*oi.UnitPrice) AS TotalSales
        FROM OrderItems oi JOIN MenuItems m ON oi.ItemID=m.ItemID GROUP BY m.Type ORDER BY TotalSales DESC, m.Type""",
    "popular_items": """SELECT m.ItemID,m.ItemName,m.Type,COALESCE(SUM(oi.Quantity),0) AS QuantitySold,
        COALESCE(SUM(oi.Quantity*oi.UnitPrice),0) AS ItemSales FROM MenuItems m LEFT JOIN OrderItems oi ON m.ItemID=oi.ItemID
        GROUP BY m.ItemID,m.ItemName,m.Type ORDER BY QuantitySold DESC,m.ItemID""",
    "least_popular_items": """SELECT m.ItemID,m.ItemName,m.Type,COALESCE(SUM(oi.Quantity),0) AS QuantitySold,
        COALESCE(SUM(oi.Quantity*oi.UnitPrice),0) AS ItemSales FROM MenuItems m LEFT JOIN OrderItems oi ON m.ItemID=oi.ItemID
        GROUP BY m.ItemID,m.ItemName,m.Type ORDER BY QuantitySold,m.ItemID LIMIT 5""",
    "daily_sales": "SELECT OrderDate AS SalesDate,COUNT(*) AS TotalOrders,SUM(TotalCost) AS TotalSales FROM Orders GROUP BY OrderDate ORDER BY OrderDate",
    "delivery_status": """SELECT COALESCE(d.DeliveryStatus,'Unassigned') AS DeliveryStatus,
        COUNT(*) AS TotalOrders,SUM(o.TotalCost) AS TotalSales FROM Orders o
        LEFT JOIN OrderDeliveryStatus d ON o.OrderID=d.OrderID
        GROUP BY COALESCE(d.DeliveryStatus,'Unassigned') ORDER BY DeliveryStatus""",
    "customer_history": """SELECT c.CustomerID,c.CustomerName,o.OrderID,o.OrderDate,o.TableNo,o.TotalCost,d.DeliveryStatus
        FROM Customers c JOIN Orders o ON c.CustomerID=o.CustomerID
        LEFT JOIN OrderDeliveryStatus d ON o.OrderID=d.OrderID ORDER BY c.CustomerID,o.OrderDate,o.OrderID""",
    "top_customers": """SELECT c.CustomerID,c.CustomerName,COUNT(o.OrderID) AS TotalOrders,SUM(o.TotalCost) AS TotalSpent
        FROM Customers c JOIN Orders o ON c.CustomerID=o.CustomerID GROUP BY c.CustomerID,c.CustomerName
        ORDER BY TotalSpent DESC,c.CustomerID LIMIT 5""",
    "booking_count": "SELECT COUNT(*) AS TotalBookings FROM Bookings",
    "booking_activity": "SELECT BookingDate,COUNT(*) AS BookingCount FROM Bookings GROUP BY BookingDate ORDER BY BookingDate",
    "highest_sale": "SELECT OrderID,CustomerID,OrderDate,TotalCost FROM Orders WHERE TotalCost=(SELECT MAX(TotalCost) FROM Orders) ORDER BY OrderID",
    "lowest_sale": "SELECT OrderID,CustomerID,OrderDate,TotalCost FROM Orders WHERE TotalCost=(SELECT MIN(TotalCost) FROM Orders) ORDER BY OrderID",
    "repeat_customers": """SELECT c.CustomerID,c.CustomerName,COUNT(o.OrderID) AS TotalOrders,SUM(o.TotalCost) AS TotalSpent
        FROM Customers c JOIN Orders o ON c.CustomerID=o.CustomerID GROUP BY c.CustomerID,c.CustomerName
        HAVING COUNT(o.OrderID)>=2 ORDER BY TotalSpent DESC,c.CustomerID""",
    "revenue_trends": """WITH monthly AS (
        SELECT DATE_FORMAT(OrderDate,'%Y-%m') AS SalesMonth,COUNT(*) AS TotalOrders,SUM(TotalCost) AS TotalSales
        FROM Orders GROUP BY DATE_FORMAT(OrderDate,'%Y-%m')
        ), changes AS (
        SELECT *,LAG(TotalSales) OVER (ORDER BY SalesMonth) AS PreviousSales FROM monthly
        ) SELECT *,TotalSales-PreviousSales AS RevenueChange,
        ROUND(100*(TotalSales-PreviousSales)/NULLIF(PreviousSales,0),2) AS ChangePercent FROM changes ORDER BY SalesMonth""",
}


def run_report(pool, name):
    if name not in REPORT_QUERIES:
        raise ValueError("Unknown report name.")
    with pooled_cursor(pool, dictionary=True) as (_, cursor):
        cursor.execute(REPORT_QUERIES[name])
        rows = cursor.fetchall()
    return rows


def print_table(title, rows):
    print("\n" + title)
    if not rows:
        print("No records.")
        return
    columns = list(rows[0])
    formatted = [[str(row[col]) if row[col] is not None else "N/A" for col in columns] for row in rows]
    widths = [max(len(col), *(len(row[i]) for row in formatted)) for i,col in enumerate(columns)]
    print(" | ".join(col.ljust(width) for col,width in zip(columns,widths)))
    print("-+-".join("-"*width for width in widths))
    for row in formatted:
        print(" | ".join(value.ljust(width) for value,width in zip(row,widths)))


def write_text_atomic(path, content):
    """Replace a text artifact only after its complete contents reach disk."""
    path = Path(path)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent,
                prefix=f".{path.name}.", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        if path.exists():
            temporary_path.chmod(stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary_path, path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def write_report(pool):
    """Create JSON, Markdown and an SVG plot from the same actual query results."""
    reports = {name: run_report(pool, name) for name in REPORT_QUERIES}
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    write_text_atomic(output / "sales_report.json", json.dumps(reports, indent=2, default=str) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    trends = reports["revenue_trends"]
    fig, ax = plt.subplots(figsize=(9,4.4), layout="constrained")
    ax.bar([row["SalesMonth"] for row in trends], [float(row["TotalSales"]) for row in trends], color="#24483e")
    ax.set(title="Little Lemon demonstration sales by month", xlabel="Order month", ylabel="Sales (USD)")
    ax.spines[["top","right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(output / "monthly_sales.svg", metadata={"Creator": "Abdulrahman M. Yaqyn", "Date": None})
    plt.close(fig)
    lines = ["# Little Lemon Analysis and Sales Report", "", "All records are fictional demonstration data. This is not the official course dataset or real restaurant revenue.", "",
             "Amounts are USD. Revenue uses historical order-item quantities and unit prices; stored order totals are reconciled before reporting. No tax, tips, refunds, food costs, or profit figures are modeled.", "",
             "![Demonstration sales by month](output/monthly_sales.svg)", ""]
    for name, rows in reports.items():
        lines += ["## " + name.replace("_"," ").capitalize(), ""]
        if rows:
            columns = list(rows[0])
            lines += ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
            lines += ["| " + " | ".join(str(row[col]).replace("|", "\\|") if row[col] is not None else "N/A" for col in columns) + " |" for row in rows]
        else:
            lines += ["No records."]
        lines += [""]
    lines += ["## Interpretation and limits", "", "This sample spans selected dates rather than a complete trading history. Month-to-month changes describe only these demonstration records. Zero-quantity menu items have no recorded orders in this dataset; this is not evidence of real customer preferences. Sales are gross recorded order values, not profit. CancelBooking refuses bookings linked to orders so sales history remains intact.", ""]
    write_text_atomic(ROOT / "REPORT.md", "\n".join(lines))
    print("Restaurant sales report saved to REPORT.md and output/.")
    return reports
