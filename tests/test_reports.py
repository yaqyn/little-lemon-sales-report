"""Financial reports reconcile to independent line-item arithmetic and sample facts."""
from decimal import Decimal, ROUND_HALF_UP

from src.reports import REPORT_QUERIES, run_report
from tests.support import MySQLIntegrationCase


REQUIRED_REPORTS = {'summary', 'category_sales', 'popular_items', 'least_popular_items',
                    'daily_sales', 'customer_history', 'top_customers', 'booking_activity',
                    'revenue_trends', 'booking_count', 'highest_sale', 'lowest_sale',
                    'repeat_customers', 'delivery_status'}


class ReportIntegrationTests(MySQLIntegrationCase):
    def test_all_required_reports_execute(self):
        self.assertTrue(REQUIRED_REPORTS.issubset(REPORT_QUERIES))
        for name in sorted(REQUIRED_REPORTS):
            with self.subTest(report=name):
                rows = run_report(self.pool, name)
                self.assertIsInstance(rows, list)
                self.assertTrue(all(isinstance(row, dict) for row in rows))

    def test_summary_matches_independent_line_item_arithmetic(self):
        summary = run_report(self.pool, 'summary')[0]
        prices = self.query('SELECT Quantity,UnitPrice FROM OrderItems')
        line_sales = sum((Decimal(quantity) * unit_price for quantity, unit_price in prices), Decimal('0.00'))
        order_totals = [row[0] for row in self.query('SELECT TotalCost FROM Orders')]
        self.assertEqual(summary['TotalSales'], line_sales)
        self.assertEqual(summary['TotalOrders'], len(order_totals))
        self.assertEqual(summary['HighestOrderValue'], max(order_totals))
        self.assertEqual(summary['LowestOrderValue'], min(order_totals))
        self.assertEqual(summary['AverageOrderValue'],
                         (line_sales / len(order_totals)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        expected = self.demo_expected()['sales']
        self.assertEqual(summary['TotalOrders'], expected['TotalOrders'])
        for key in ['TotalSales', 'AverageOrderValue', 'HighestOrderValue', 'LowestOrderValue']:
            self.assertEqual(summary[key], Decimal(expected[key]))

    def test_order_totals_match_the_demonstration_manifest(self):
        totals = {str(row[0]): str(row[1]) for row in self.query('SELECT OrderID,TotalCost FROM Orders')}
        self.assertEqual(totals, self.demo_expected()['order_totals'])

    def test_category_sales_reconcile_to_restaurant_sales(self):
        rows = run_report(self.pool, 'category_sales')
        actual = {row['Type']: str(row['TotalSales']) for row in rows}
        self.assertEqual(actual, self.demo_expected()['category_sales'])
        self.assertEqual(sum(row['TotalSales'] for row in rows),
                         run_report(self.pool, 'summary')[0]['TotalSales'])

    def test_menu_popularity_and_unsold_item_are_reported(self):
        most = run_report(self.pool, 'popular_items')
        least = run_report(self.pool, 'least_popular_items')
        quantities = {str(row['ItemID']): int(row['QuantitySold']) for row in most}
        sales = {str(row['ItemID']): str(row['ItemSales']) for row in most}
        self.assertEqual(quantities, self.demo_expected()['item_quantities'])
        self.assertEqual(sales, self.demo_expected()['item_sales'])
        self.assertEqual([int(row['QuantitySold']) for row in most],
                         sorted(quantities.values(), reverse=True))
        self.assertEqual(int(least[0]['QuantitySold']), 0)
        self.assertEqual(least[0]['ItemID'], 3010)

    def test_daily_sales_match_expected_dates_and_totals(self):
        rows = run_report(self.pool, 'daily_sales')
        actual = {str(row['SalesDate']): str(row['TotalSales']) for row in rows}
        self.assertEqual(actual, self.demo_expected()['sales_by_date'])

    def test_delivery_status_totals_reconcile_to_all_orders(self):
        rows = run_report(self.pool, 'delivery_status')
        summary = run_report(self.pool, 'summary')[0]
        self.assertEqual(sum(row['TotalOrders'] for row in rows), summary['TotalOrders'])
        self.assertEqual(sum(row['TotalSales'] for row in rows), summary['TotalSales'])
        self.assertEqual(
            [row['DeliveryStatus'] for row in rows],
            sorted(row['DeliveryStatus'] for row in rows),
        )

    def test_monthly_revenue_trend_preserves_total_sales(self):
        rows = run_report(self.pool, 'revenue_trends')
        actual = {str(row['SalesMonth']): str(row['TotalSales']) for row in rows}
        self.assertEqual(actual, self.demo_expected()['sales_by_month'])
        self.assertEqual(sum(row['TotalSales'] for row in rows), Decimal('835.00'))

    def test_customers_are_ranked_by_actual_spending(self):
        rows = run_report(self.pool, 'top_customers')
        actual = {str(row['CustomerID']): str(row['TotalSpent']) for row in rows}
        expected = dict(sorted(self.demo_expected()['customer_totals'].items(),
                               key=lambda item: Decimal(item[1]), reverse=True)[:5])
        self.assertEqual(actual, expected)
        self.assertEqual(rows[0]['CustomerID'], 1001)
        self.assertEqual(rows[0]['TotalSpent'], Decimal('245.50'))
        self.assertEqual([row['TotalSpent'] for row in rows], sorted((row['TotalSpent'] for row in rows), reverse=True))

    def test_customer_order_history_and_repeat_customers(self):
        rows = run_report(self.pool, 'customer_history')
        counts = {}
        for row in rows:
            customer = str(row['CustomerID'])
            counts[customer] = counts.get(customer, 0) + 1
        self.assertEqual(counts, self.demo_expected()['customer_order_counts'])
        repeats = run_report(self.pool, 'repeat_customers')
        self.assertEqual({row['CustomerID'] for row in repeats}, {1001, 1002, 1003})

    def test_booking_counts_and_activity_match_seeded_records(self):
        total = run_report(self.pool, 'booking_count')[0]['TotalBookings']
        self.assertEqual(total, self.demo_expected()['table_counts']['Bookings'])
        rows = run_report(self.pool, 'booking_activity')
        actual = {str(row['BookingDate']): int(row['BookingCount']) for row in rows}
        self.assertEqual(actual, self.demo_expected()['booking_dates'])
        self.assertEqual(sum(row['BookingCount'] for row in rows), total)

    def test_highest_and_lowest_transactions_are_identified(self):
        highest = run_report(self.pool, 'highest_sale')[0]
        lowest = run_report(self.pool, 'lowest_sale')[0]
        self.assertEqual(highest['OrderID'], 5012)
        self.assertEqual(highest['TotalCost'], Decimal('112.50'))
        self.assertEqual(lowest['OrderID'], 5002)
        self.assertEqual(lowest['TotalCost'], Decimal('31.00'))
