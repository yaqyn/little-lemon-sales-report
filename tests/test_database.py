"""Real schema, safe seeding, and transaction durability checks."""
from src.connection_pool import pooled_cursor
from src.database import initialize_database, seed_database, validate_data
from tests.support import MySQLIntegrationCase


TABLES = {'Customers', 'Bookings', 'Employees', 'MenuItems', 'Orders', 'OrderItems', 'OrderDeliveryStatus'}


class DatabaseIntegrationTests(MySQLIntegrationCase):
    def test_all_required_tables_exist(self):
        rows = self.query('SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()')
        self.assertTrue(TABLES.issubset({row[0] for row in rows}))

    def test_foreign_keys_are_present(self):
        count = self.query("SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS "
                           "WHERE CONSTRAINT_SCHEMA=DATABASE() AND CONSTRAINT_TYPE='FOREIGN KEY'")[0][0]
        self.assertGreaterEqual(count, 7)

    def test_seed_is_safe_to_rerun(self):
        before = {table: self.query(f'SELECT COUNT(*) FROM `{table}`')[0][0] for table in TABLES}
        initialize_database(self.pool)
        seed_database(self.pool)
        seed_database(self.pool)
        after = {table: self.query(f'SELECT COUNT(*) FROM `{table}`')[0][0] for table in TABLES}
        self.assertEqual(after, before)

    def test_inserted_data_has_consistent_totals_and_relationships(self):
        validation = validate_data(self.pool)
        self.assertEqual(validation['order_total_mismatches'], [])
        self.assertEqual(validation['foreign_key_violations'], 0)
        self.assertTrue(all(validation['row_counts'][table] > 0 for table in TABLES))

    def test_explicit_commit_is_visible_to_another_connection(self):
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        try:
            with pooled_cursor(self.pool) as (connection, cursor):
                cursor.execute('INSERT INTO Bookings '
                               '(BookingID,BookingDate,BookingSlot,TableNo,CustomerID,EmployeeID) '
                               'VALUES (%s,%s,%s,%s,%s,%s)',
                               (booking_id, day, '11:00:00', 1, customer_id, employee_id))
                connection.commit()
                with pooled_cursor(self.pool) as (_, other_cursor):
                    other_cursor.execute('SELECT CustomerID FROM Bookings WHERE BookingID=%s', (booking_id,))
                    self.assertEqual(other_cursor.fetchone()[0], customer_id)
        finally:
            self.remove_test_booking(booking_id)

    def test_rollback_does_not_persist_an_insert(self):
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        with pooled_cursor(self.pool) as (connection, cursor):
            cursor.execute('INSERT INTO Bookings '
                           '(BookingID,BookingDate,BookingSlot,TableNo,CustomerID,EmployeeID) '
                           'VALUES (%s,%s,%s,%s,%s,%s)',
                           (booking_id, day, '11:00:00', 1, customer_id, employee_id))
            connection.rollback()
        self.assertEqual(self.query('SELECT BookingID FROM Bookings WHERE BookingID=%s', (booking_id,)), [])

    def test_seeded_table_counts_match_manifest(self):
        for table, expected in self.demo_expected()['table_counts'].items():
            with self.subTest(table=table):
                self.assertEqual(self.query(f'SELECT COUNT(*) FROM `{table}`')[0][0], expected)

    def test_sql_error_rolls_back_earlier_writes(self):
        from mysql.connector import Error
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        try:
            with self.assertRaises(Error):
                with pooled_cursor(self.pool) as (_, cursor):
                    cursor.execute('INSERT INTO Bookings '
                                   '(BookingID,BookingDate,BookingSlot,TableNo,CustomerID,EmployeeID) '
                                   'VALUES (%s,%s,%s,%s,%s,%s)',
                                   (booking_id, day, '11:00:00', 1, customer_id, employee_id))
                    cursor.execute('SELECT MissingTransactionFixtureColumn FROM Bookings')
            self.assertEqual(self.query('SELECT BookingID FROM Bookings WHERE BookingID=%s', (booking_id,)), [])
        finally:
            self.remove_test_booking(booking_id)
