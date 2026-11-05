"""Shared integration fixtures; never connects to or edits the Django schema."""
from datetime import date, timedelta
import json
import os
from pathlib import Path
import secrets
import unittest

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {**dotenv_values(ROOT / '.env'), **os.environ}
MYSQL_CONFIGURED = bool(SETTINGS.get('MYSQL_USER')) and 'MYSQL_PASSWORD' in SETTINGS
NOT_VERIFIED = 'NOT VERIFIED: configure MYSQL_USER and MYSQL_PASSWORD for real MySQL integration tests.'


@unittest.skipUnless(MYSQL_CONFIGURED, NOT_VERIFIED)
class MySQLIntegrationCase(unittest.TestCase):
    """Configured connection failures remain failures, not skipped tests."""

    @classmethod
    def setUpClass(cls):
        from src.connection_pool import create_pool
        from src.database import initialize_database, seed_database
        from src.procedures import create_procedures
        cls.pool = create_pool()
        initialize_database(cls.pool)
        seed_database(cls.pool)
        create_procedures(cls.pool)

    def query(self, statement, parameters=()):
        from src.connection_pool import pooled_cursor
        with pooled_cursor(self.pool) as (_, cursor):
            cursor.execute(statement, parameters)
            return cursor.fetchall()

    def demo_expected(self):
        return json.loads((ROOT / 'data' / 'demo_expected.json').read_text())

    def booking_fixture(self):
        """Choose a new identifier/slot instead of reusing a sample booking."""
        customer_id = self.query('SELECT CustomerID FROM Customers ORDER BY CustomerID LIMIT 1')[0][0]
        employee_id = self.query('SELECT EmployeeID FROM Employees ORDER BY EmployeeID LIMIT 1')[0][0]
        while True:
            booking_id = 800_000_000 + secrets.randbelow(100_000_000)
            day = date.today() + timedelta(days=90 + secrets.randbelow(10_000))
            occupied = self.query(
                'SELECT BookingID FROM Bookings WHERE BookingID=%s OR '
                '(BookingDate=%s AND BookingSlot=%s AND TableNo=%s)',
                (booking_id, day, '11:00:00', 1),
            )
            if not occupied:
                return booking_id, day, customer_id, employee_id

    def remove_test_booking(self, booking_id):
        from src.connection_pool import pooled_cursor
        with pooled_cursor(self.pool) as (connection, cursor):
            cursor.execute('DELETE FROM Bookings WHERE BookingID=%s', (booking_id,))
            connection.commit()
