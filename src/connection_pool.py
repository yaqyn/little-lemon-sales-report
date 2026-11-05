"""A two-slot connection pool restricted to the separate sales database."""
import os
from contextlib import contextmanager
from pathlib import Path

import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATABASE_NAME = "little_lemon_sales"


def load_config():
    load_dotenv(ROOT / ".env")
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", ""),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", DATABASE_NAME),
    }
    if config["database"] != DATABASE_NAME:
        raise ValueError("MYSQL_DATABASE must be little_lemon_sales; other schemas are refused.")
    if not config["user"] or not config["password"]:
        raise ValueError("Set MYSQL_USER and MYSQL_PASSWORD in the environment or private .env.")
    return config


def create_pool(config=None):
    dbconfig = dict(load_config() if config is None else config)
    if dbconfig.pop("database", DATABASE_NAME) != DATABASE_NAME:
        raise ValueError("Only the separate little_lemon_sales database is allowed.")
    print("Connecting to MySQL database...")
    print("Creating connection pool...")
    try:
        # Omit database only for initial CREATE DATABASE through a pooled connection.
        pool = MySQLConnectionPool(
            pool_name="pool_a", pool_size=2, pool_reset_session=True,
            autocommit=False, charset="utf8mb4", connection_timeout=10,
            time_zone="+00:00", **dbconfig,
        )
    except Error as er:
        print("Error code:", er.errno)
        print("Error message:", er.msg)
        raise
    print("Connection established successfully.")
    print("The connection pool is created with a name:", pool.pool_name)
    print("The pool size is:", pool.pool_size)
    return pool


@contextmanager
def pooled_cursor(pool, use_database=True, dictionary=False):
    """Always close the cursor and return the connection, including failure paths.

    The caller commits intentional writes. Any remaining transaction is rolled
    back on exit; pooled sockets stay available for reuse until the process ends.
    """
    connection = cursor = None
    try:
        connection = pool.get_connection()
        print("Connection acquired from pool.")
        if use_database:
            connection.cmd_init_db(DATABASE_NAME)
        cursor = connection.cursor(dictionary=dictionary)
        yield connection, cursor
    except Error as er:
        print("Error code:", er.errno)
        print("Error message:", er.msg)
        raise
    finally:
        try:
            if cursor is not None:
                print("Closing cursor...")
                cursor.close()
        finally:
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.rollback()
                        print("Uncommitted transaction rolled back.")
                finally:
                    connection.close()
                    print("Returning connection to pool...")
