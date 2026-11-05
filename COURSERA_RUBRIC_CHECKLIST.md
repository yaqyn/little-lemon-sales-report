# Coursera rubric verification

Assignment: Little Lemon Analysis and Sales Report. Verified on 5 November 2026
using an actual MySQL 8.4.13 server and MySQL Connector/Python 26.10.0.
All restaurant records are demonstration data, not the unavailable official course
dataset. This checklist verifies the seven supplied rubric items; it does not
claim coverage of additional original lab tasks that were not supplied.

| Requirement | Status | Executed evidence |
| --- | --- | --- |
| 1. Connection pool created and used | **PASS** | `src/connection_pool.py:create_pool` constructs `MySQLConnectionPool(pool_name="pool_a", pool_size=2)`. Notebook section 4 printed `The connection pool is created with a name: pool_a` and `The pool size is: 2`. `test_actual_connection_and_mysql_version`, `test_pool_is_named_pool_a_and_size_two`, and `test_two_connections_exhaust_pool_and_returning_one_restores_capacity` passed against MySQL. |
| 2. Database and all required tables created | **PASS** | `initialize_database` creates only `little_lemon_sales`; section 5 printed the actual selected database and seven table names. `test_all_required_tables_exist` and `test_foreign_keys_are_present` passed. DDL is non-destructive, implicitly committed by MySQL, and separate from data transactions. |
| 3. Tables populated with records | **PASS** | Section 7 validated Customers=8, Employees=4, MenuItems=10, Bookings=12, Orders=12, OrderItems=36, OrderDeliveryStatus=12. `test_seeded_table_counts_match_manifest` and `test_seed_is_safe_to_rerun` passed. All 94 records are labeled fictional demonstration data. |
| 4. Database changes committed | **PASS** | `execute_sql_script` commits the seed transaction. Section 13 calls `connection.commit()` and a second pooled connection confirms persistence, then demonstrates rollback. `test_explicit_commit_is_visible_to_another_connection`, `test_rollback_does_not_persist_an_insert`, and `test_sql_error_rolls_back_earlier_writes` passed. |
| 5. Stored procedures created and used | **PASS** | All eight routines appear in `information_schema.ROUTINES`; notebook section 9 executed each via `cursor.callproc` through the helper, and section 10 directly iterates `cursor.stored_results()`. All 12 procedure tests passed, including `test_all_eight_procedures_exist_and_creation_is_rerunnable` and `test_manage_update_and_cancel_booking_commit_successfully`. |
| 6. Python print statements show progress | **PASS** | Saved notebook outputs include `Connection established successfully.`, `Database tables created successfully.`, `Records committed successfully.`, `Executing sales report procedure...`, and the actual report values. Failure-output tests confirm a failed pool does not print a success claim. |
| 7. Connections returned to pool | **PASS** | `pooled_cursor` closes its cursor and returns the connection in nested `finally` blocks. Notebook section 14 handles an actual SQL error, then reacquires both slots and prints `All acquired connections returned to pool.` Mock and real-pool cleanup tests passed, including `test_sql_failure_returns_connection_to_real_pool` and `test_cursor_close_failure_does_not_leak_connection`. |

**Result: 7 PASS, 0 FAIL, 0 NOT VERIFIED for the supplied rubric.**

## Execution record

- `python -m unittest discover -v`: **44 passed**, 0 failures, 0 errors,
  0 skipped. This includes 35 real MySQL integration tests and 9 unit tests.
- `python scripts/execute_notebook.py`: executed successfully **three times**;
  16 explained sections and 14 executable code cells; 0 unexpected exceptions.
- Seed setup and procedure creation were rerun without duplicate records.
- Report reconciliation: **12 orders**, **USD 835.00** total, **USD 69.58** average,
  **USD 112.50** highest, **USD 31.00** lowest, maximum line quantity **6**.
- Missing-credentials mode was checked separately: 9 unit tests passed and the
  35 database tests explicitly skipped as **NOT VERIFIED**. This fallback run
  is not counted as a MySQL verification pass.
- No browser or interactive Jupyter UI session is claimed. The notebook was run
  by a real Python 3.14.8 Jupyter kernel using nbclient.

Machine-readable evidence: [verification.json](evidence/verification.json) and
[notebook_execution.json](evidence/notebook_execution.json). Source/data protection:
[django_preservation.json](evidence/django_preservation.json).

## Scope and limitations

Stored procedures never commit internally: Python controls transaction boundaries.
Only temporary demonstration/test bookings are changed or deleted. Bookings tied
to orders are protected so sales history remains intact. Returning a pooled
connection releases the logical checkout; pooled physical sockets remain reusable
until the process/kernel ends.

Connector/Python 26.10 deprecates `stored_results()`. The method is retained and
executed because the supplied assignment explicitly requires it; dependency
versions are pinned. The original Django project was not changed or pushed to.
All 69 tracked files and the contents of its 14 tables matched before/after
fingerprints. Private credentials and database records are excluded from evidence
and the ZIP.
