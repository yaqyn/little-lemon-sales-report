"""Stored routine creation and invocation with caller-owned transactions."""
from .connection_pool import pooled_cursor
from .database import execute_sql_script

PROCEDURES = (
    "GetMaxQuantity", "ManageBooking", "UpdateBooking", "CancelBooking",
    "GetSalesReport", "GetCustomerOrders", "GetPopularMenuItems", "GetEmployeeBookings",
)


def create_procedures(pool):
    execute_sql_script(pool, "stored_procedures.sql")
    print("Stored procedures created successfully; existing definitions preserved.")


def call_procedure(pool, name, args=(), commit=False):
    if name not in PROCEDURES:
        raise ValueError("Unknown project procedure.")
    print("Executing procedure:", name)
    result_sets = []
    with pooled_cursor(pool) as (connection, cursor):
        cursor.callproc(name, args)
        for result in cursor.stored_results():
            try:
                rows = result.fetchall()
                result_sets.append(rows)
                for row in rows:
                    print(row)
            finally:
                result.close()
        if commit:
            connection.commit()
            print("Records committed successfully.")
    return result_sets
