"""Pool size, return semantics, and error paths with and without a server."""
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import MagicMock, patch

from mysql.connector import Error
from mysql.connector.errors import PoolError

from src.connection_pool import create_pool, pooled_cursor, validate_config
from tests.support import MySQLIntegrationCase


class PoolCleanupUnitTests(unittest.TestCase):
    def make_pool(self):
        pool = MagicMock()
        connection = pool.get_connection.return_value
        cursor = connection.cursor.return_value
        return pool, connection, cursor

    def test_normal_cursor_exit_returns_the_connection(self):
        pool, connection, cursor = self.make_pool()
        with pooled_cursor(pool) as (acquired, active_cursor):
            self.assertIs(acquired, connection)
            self.assertIs(active_cursor, cursor)
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_sql_error_rolls_back_and_returns_connection(self):
        pool, connection, cursor = self.make_pool()
        cursor.execute.side_effect = Error(msg='Deliberate fixture failure', errno=1644)
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(Error):
            with pooled_cursor(pool) as (_, active):
                active.execute('fixture statement')
        connection.rollback.assert_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()
        self.assertIn('1644', output.getvalue())
        self.assertIn('Deliberate fixture failure', output.getvalue())

    def test_python_error_also_releases_resources(self):
        pool, connection, cursor = self.make_pool()
        with self.assertRaisesRegex(ValueError, 'fixture'):
            with pooled_cursor(pool):
                raise ValueError('fixture')
        connection.rollback.assert_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_cursor_creation_failure_still_returns_connection(self):
        pool, connection, _ = self.make_pool()
        connection.cursor.side_effect = Error(msg='Cursor fixture failure', errno=2000)
        with self.assertRaises(Error):
            with pooled_cursor(pool):
                self.fail('The cursor was not created.')
        connection.close.assert_called_once()

    def test_cursor_close_failure_does_not_leak_connection(self):
        pool, connection, cursor = self.make_pool()
        cursor.close.side_effect = Error(msg='Close fixture failure', errno=2000)
        with self.assertRaises(Error):
            with pooled_cursor(pool):
                pass
        connection.close.assert_called_once()

    def test_pool_exhaustion_has_no_resource_to_close(self):
        pool = MagicMock()
        pool.get_connection.side_effect = PoolError(msg='Pool fixture exhausted', errno=2024)
        with self.assertRaises(PoolError):
            with pooled_cursor(pool):
                self.fail('The exhausted pool must not yield.')
        pool.get_connection.assert_called_once()

    def test_programmatic_config_rejects_the_django_database(self):
        config = {'host': '127.0.0.1', 'port': 3306, 'user': 'fixture',
                  'password': 'fixture-only-value', 'database': 'littlelemon'}
        with patch('src.connection_pool.MySQLConnectionPool') as constructor:
            with self.assertRaises(ValueError):
                create_pool(config)
            constructor.assert_not_called()

    def test_connection_config_is_normalized_before_pool_creation(self):
        config = {'host': ' db.internal ', 'port': '3307', 'user': ' analyst ',
                  'password': 'fixture-only-value', 'database': 'little_lemon_sales'}
        validated = validate_config(config)
        self.assertEqual(validated['host'], 'db.internal')
        self.assertEqual(validated['port'], 3307)
        self.assertEqual(validated['user'], 'analyst')
        self.assertEqual(config['host'], ' db.internal ')

    def test_invalid_connection_settings_fail_before_mysql_is_contacted(self):
        base = {'host': '127.0.0.1', 'port': 3306, 'user': 'fixture',
                'password': 'fixture-only-value', 'database': 'little_lemon_sales'}
        invalid = [
            ({**base, 'host': ' '}, 'MYSQL_HOST'),
            ({**base, 'port': 'not-a-port'}, 'MYSQL_PORT'),
            ({**base, 'port': 0}, 'MYSQL_PORT'),
            ({**base, 'port': 65536}, 'MYSQL_PORT'),
            ({**base, 'port': True}, 'MYSQL_PORT'),
            ({**base, 'user': ''}, 'MYSQL_USER'),
        ]
        with patch('src.connection_pool.MySQLConnectionPool') as constructor:
            for config, message in invalid:
                with self.subTest(config=config), self.assertRaisesRegex(ValueError, message):
                    create_pool(config)
            constructor.assert_not_called()


    def test_failed_pool_creation_reports_error_without_claiming_success(self):
        config = {'host': '127.0.0.1', 'port': 3306, 'user': 'fixture',
                  'password': 'fixture-secret-not-output', 'database': 'little_lemon_sales'}
        output = StringIO()
        with patch('src.connection_pool.MySQLConnectionPool',
                   side_effect=Error(msg='Access denied fixture', errno=1045)):
            with redirect_stdout(output), self.assertRaises(Error):
                create_pool(config)
        self.assertIn('1045', output.getvalue())
        self.assertIn('Access denied fixture', output.getvalue())
        self.assertNotIn('Connection established successfully.', output.getvalue())
        self.assertNotIn(config['password'], output.getvalue())

    def test_pool_bootstrap_omits_database_until_creation(self):
        config = {'host': '127.0.0.1', 'port': 3306, 'user': 'fixture',
                  'password': 'fixture-secret-not-output', 'database': 'little_lemon_sales'}
        with patch('src.connection_pool.MySQLConnectionPool') as constructor:
            constructor.return_value.pool_name = 'pool_a'
            constructor.return_value.pool_size = 2
            with redirect_stdout(StringIO()):
                create_pool(config)
            arguments = constructor.call_args.kwargs
            self.assertEqual(arguments['pool_name'], 'pool_a')
            self.assertEqual(arguments['pool_size'], 2)
            self.assertNotIn('database', arguments)


class PoolIntegrationTests(MySQLIntegrationCase):
    def test_actual_connection_and_mysql_version(self):
        row = self.query('SELECT DATABASE(), VERSION()')[0]
        self.assertEqual(row[0], 'little_lemon_sales')
        self.assertGreaterEqual(int(row[1].split('.')[0]), 8)

    def test_pool_is_named_pool_a_and_size_two(self):
        self.assertEqual(self.pool.pool_name, 'pool_a')
        self.assertEqual(self.pool.pool_size, 2)

    def test_two_connections_exhaust_pool_and_returning_one_restores_capacity(self):
        first = second = replacement = None
        try:
            first = self.pool.get_connection()
            second = self.pool.get_connection()
            with self.assertRaises(PoolError):
                self.pool.get_connection()
            first.close()
            first = None
            replacement = self.pool.get_connection()
            self.assertTrue(replacement.is_connected())
        finally:
            for connection in (first, second, replacement):
                if connection is not None:
                    connection.close()

    def test_sql_failure_returns_connection_to_real_pool(self):
        with self.assertRaises(Error):
            with pooled_cursor(self.pool) as (_, cursor):
                cursor.execute('SELECT DefinitelyMissingColumn FROM Customers')
        first = second = None
        try:
            first = self.pool.get_connection()
            second = self.pool.get_connection()
            self.assertTrue(first.is_connected() and second.is_connected())
        finally:
            for connection in (first, second):
                if connection is not None:
                    connection.close()
