"""Stored procedure calls use real pooled connections and isolated test bookings."""
from datetime import date, timedelta
from decimal import Decimal

from mysql.connector import Error

from src.procedures import call_procedure, create_procedures
from tests.support import MySQLIntegrationCase


PROCEDURES = {'GetMaxQuantity', 'ManageBooking', 'UpdateBooking', 'CancelBooking',
              'GetSalesReport', 'GetCustomerOrders', 'GetPopularMenuItems', 'GetEmployeeBookings'}


class ProcedureIntegrationTests(MySQLIntegrationCase):
    def test_all_eight_procedures_exist_and_creation_is_rerunnable(self):
        create_procedures(self.pool)
        rows = self.query("SELECT ROUTINE_NAME FROM information_schema.ROUTINES "
                          "WHERE ROUTINE_SCHEMA=DATABASE() AND ROUTINE_TYPE='PROCEDURE'")
        self.assertTrue(PROCEDURES.issubset({row[0] for row in rows}))

    def test_max_quantity_returns_expected_value(self):
        sets = call_procedure(self.pool, 'GetMaxQuantity')
        self.assertEqual(sets[0][0][0], self.demo_expected()['max_quantity'])

    def test_sales_procedure_returns_expected_financial_statistics(self):
        row = call_procedure(self.pool, 'GetSalesReport')[0][0]
        expected = self.demo_expected()['sales']
        self.assertEqual(row[0], expected['TotalOrders'])
        self.assertEqual(tuple(Decimal(str(value)) for value in row[1:]),
                         tuple(Decimal(expected[key]) for key in
                               ['TotalSales', 'AverageOrderValue', 'HighestOrderValue', 'LowestOrderValue']))

    def test_customer_orders_procedure_returns_only_requested_customer(self):
        customer = self.demo_expected()['demo_customer_id']
        rows = call_procedure(self.pool, 'GetCustomerOrders', (customer,))[0]
        self.assertEqual(len(rows), self.demo_expected()['customer_order_counts'][str(customer)])
        self.assertTrue(all(row[0] == customer for row in rows))
        self.assertEqual(call_procedure(self.pool, 'GetCustomerOrders', (899_999_999,))[0], [])

    def test_popular_menu_procedure_includes_unsold_items(self):
        rows = call_procedure(self.pool, 'GetPopularMenuItems')[0]
        quantities = {str(row[0]): int(row[3]) for row in rows}
        self.assertEqual(quantities, self.demo_expected()['item_quantities'])
        self.assertEqual(int(rows[0][3]), max(quantities.values()))
        self.assertEqual(int(rows[-1][3]), 0)

    def test_employee_booking_procedure_matches_assignments(self):
        rows = call_procedure(self.pool, 'GetEmployeeBookings')[0]
        expected_pairs = set(self.query('SELECT EmployeeID, BookingID FROM Bookings'))
        self.assertEqual({(row[0], row[3]) for row in rows}, expected_pairs)

    def test_manage_update_and_cancel_booking_commit_successfully(self):
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        try:
            result = call_procedure(self.pool, 'ManageBooking',
                                    (booking_id, day, '11:00:00', 1, customer_id, employee_id), commit=True)
            self.assertEqual(result[0][0][0], booking_id)
            self.assertEqual(self.query('SELECT BookingDate FROM Bookings WHERE BookingID=%s', (booking_id,))[0][0], day)
            updated_day = day + timedelta(days=1)
            call_procedure(self.pool, 'UpdateBooking', (booking_id, updated_day, '12:00:00'), commit=True)
            row = self.query('SELECT BookingDate,HOUR(BookingSlot) FROM Bookings WHERE BookingID=%s', (booking_id,))[0]
            self.assertEqual(row, (updated_day, 12))
            call_procedure(self.pool, 'CancelBooking', (booking_id,), commit=True)
            self.assertEqual(self.query('SELECT BookingID FROM Bookings WHERE BookingID=%s', (booking_id,)), [])
        finally:
            self.remove_test_booking(booking_id)

    def test_invalid_booking_inputs_are_rejected_without_insertion(self):
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        bad_arguments = [
            (booking_id, date.today() - timedelta(days=1), '11:00:00', 1, customer_id, employee_id),
            (booking_id, day, '09:00:00', 1, customer_id, employee_id),
            (booking_id, day, '11:30:00', 1, customer_id, employee_id),
            (booking_id, day, '11:00:00', 0, customer_id, employee_id),
            (booking_id, day, '11:00:00', 1, 0, employee_id),
            (booking_id, day, '11:00:00', 1, customer_id, 0),
        ]
        for args in bad_arguments:
            with self.subTest(args=args), self.assertRaises(Error):
                call_procedure(self.pool, 'ManageBooking', args, commit=True)
        self.assertEqual(self.query('SELECT BookingID FROM Bookings WHERE BookingID=%s', (booking_id,)), [])

    def test_existing_booking_id_is_never_overwritten(self):
        original = self.query('SELECT BookingID,BookingDate,BookingSlot,TableNo,CustomerID,EmployeeID '
                              'FROM Bookings ORDER BY BookingID LIMIT 1')[0]
        replacement_day = date.today() + timedelta(days=365)
        with self.assertRaises(Error):
            call_procedure(self.pool, 'ManageBooking',
                           (original[0], replacement_day, '20:00:00', 50, original[4], original[5]), commit=True)
        after = self.query('SELECT BookingID,BookingDate,BookingSlot,TableNo,CustomerID,EmployeeID '
                           'FROM Bookings WHERE BookingID=%s', (original[0],))[0]
        self.assertEqual(after, original)

    def test_booked_table_time_is_unique(self):
        booking_id, day, customer_id, employee_id = self.booking_fixture()
        second_id, _, _, _ = self.booking_fixture()
        try:
            call_procedure(self.pool, 'ManageBooking',
                           (booking_id, day, '11:00:00', 1, customer_id, employee_id), commit=True)
            with self.assertRaises(Error):
                call_procedure(self.pool, 'ManageBooking',
                               (second_id, day, '11:00:00', 1, customer_id, employee_id), commit=True)
            self.assertEqual(self.query('SELECT BookingID FROM Bookings WHERE BookingID=%s', (second_id,)), [])
        finally:
            self.remove_test_booking(booking_id)
            self.remove_test_booking(second_id)

    def test_sales_linked_bookings_cannot_be_cancelled_or_rescheduled(self):
        booking_id = self.query('SELECT BookingID FROM Orders ORDER BY OrderID LIMIT 1')[0][0]
        original = self.query('SELECT BookingDate,BookingSlot FROM Bookings WHERE BookingID=%s', (booking_id,))[0]
        with self.assertRaises(Error):
            call_procedure(self.pool, 'CancelBooking', (booking_id,), commit=True)
        with self.assertRaises(Error):
            call_procedure(self.pool, 'UpdateBooking', (booking_id, date.today() + timedelta(days=2), '13:00:00'), commit=True)
        self.assertEqual(self.query('SELECT BookingDate,BookingSlot FROM Bookings WHERE BookingID=%s', (booking_id,))[0], original)

    def test_unknown_booking_is_reported_as_error(self):
        booking_id, day, _, _ = self.booking_fixture()
        with self.assertRaises(Error):
            call_procedure(self.pool, 'CancelBooking', (booking_id,), commit=True)
        with self.assertRaises(Error):
            call_procedure(self.pool, 'UpdateBooking', (booking_id, day, '11:00:00'), commit=True)
