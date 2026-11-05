"""Non-destructive DDL and transactional, idempotent demonstration seeding."""
from pathlib import Path

from .connection_pool import DATABASE_NAME, ROOT, pooled_cursor

TABLES = ("Customers", "Employees", "MenuItems", "Bookings", "Orders", "OrderItems", "OrderDeliveryStatus")


def split_sql_script(text):
    """Read our line-terminated SQL scripts, including DELIMITER-wrapped routines.

    Unlike splitting on every semicolon, this preserves a procedure's BEGIN/END
    body. This intentionally accepts the project's controlled SQL files only.
    """
    delimiter, pending = ";", []
    for line in text.splitlines():
        if line.strip().upper().startswith("DELIMITER "):
            if any(part.strip() and not part.lstrip().startswith("--") for part in pending):
                raise ValueError("Unfinished SQL before DELIMITER.")
            pending = []
            delimiter = line.strip().split(None, 1)[1]
            continue
        pending.append(line)
        if line.rstrip().endswith(delimiter):
            statement = "\n".join(pending).rstrip()[:-len(delimiter)].strip()
            if statement:
                yield statement
            pending = []
    if any(part.strip() and not part.lstrip().startswith("--") for part in pending):
        raise ValueError("SQL script has an unfinished statement.")


def execute_sql_script(pool, filename):
    filename = Path(filename)
    path = (ROOT / "sql" / filename).resolve()
    allowed = {(ROOT / "sql" / name).resolve() for name in ("schema.sql", "seed_data.sql", "stored_procedures.sql")}
    if path not in allowed:
        raise ValueError("Only this project's three SQL scripts may be executed.")
    with pooled_cursor(pool) as (connection, cursor):
        for statement in split_sql_script(path.read_text()):
            cursor.execute(statement)
            if cursor.with_rows:
                cursor.fetchall()
            while cursor.nextset():
                if cursor.with_rows:
                    cursor.fetchall()
        connection.commit()
        print("Records committed successfully.")


def initialize_database(pool):
    with pooled_cursor(pool, use_database=False) as (connection, cursor):
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        connection.commit()
    execute_sql_script(pool, "schema.sql")
    print("Database tables created successfully.")


def seed_database(pool):
    print("Inserting restaurant demonstration data...")
    execute_sql_script(pool, "seed_data.sql")
    print("Demonstration records inserted; existing identifiers were preserved.")


def validate_data(pool):
    with pooled_cursor(pool, dictionary=True) as (_, cursor):
        counts = {}
        for table in TABLES:
            cursor.execute(f"SELECT COUNT(*) AS n FROM `{table}`")
            counts[table] = cursor.fetchone()["n"]
        cursor.execute("""
            SELECT o.OrderID, o.TotalCost, COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0) AS LineTotal
            FROM Orders o LEFT JOIN OrderItems oi ON o.OrderID = oi.OrderID
            GROUP BY o.OrderID, o.TotalCost
            HAVING o.TotalCost <> COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0)
        """)
        mismatches = cursor.fetchall()
        cursor.execute("""
            SELECT
              (SELECT COUNT(*) FROM Bookings b LEFT JOIN Customers c ON b.CustomerID=c.CustomerID WHERE c.CustomerID IS NULL) +
              (SELECT COUNT(*) FROM Bookings b LEFT JOIN Employees e ON b.EmployeeID=e.EmployeeID WHERE e.EmployeeID IS NULL) +
              (SELECT COUNT(*) FROM Orders o LEFT JOIN Bookings b ON o.BookingID=b.BookingID AND o.CustomerID=b.CustomerID AND o.TableNo=b.TableNo WHERE b.BookingID IS NULL) +
              (SELECT COUNT(*) FROM OrderItems oi LEFT JOIN Orders o ON oi.OrderID=o.OrderID WHERE o.OrderID IS NULL) +
              (SELECT COUNT(*) FROM OrderItems oi LEFT JOIN MenuItems m ON oi.ItemID=m.ItemID WHERE m.ItemID IS NULL) +
              (SELECT COUNT(*) FROM OrderDeliveryStatus d LEFT JOIN Orders o ON d.OrderID=o.OrderID WHERE o.OrderID IS NULL)
              AS Violations
        """)
        violations = cursor.fetchone()["Violations"]
    result = {"row_counts": counts, "order_total_mismatches": mismatches, "foreign_key_violations": violations}
    if mismatches or violations:
        raise ValueError(f"Sales integrity validation failed: {result}")
    print("Inserted records validated:", counts)
    print("Order totals match their line items; foreign-key violations:", violations)
    return result
