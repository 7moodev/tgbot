import os
from typing import Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from functools import wraps
from urllib.parse import urlparse
from ..commands.utils.services.log_service import LogService

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL environment variable not set")


logger = LogService("POSTGRES")


def db_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = None
        try:
            # Parse the DATABASE_URL environment variable
            result = urlparse(DATABASE_URL)
            username = result.username
            password = result.password
            database = result.path[1:]  # Remove leading slash
            hostname = result.hostname
            port = result.port

            conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port,
            )
            cursor = conn.cursor()
            result = func(self, cursor, *args, **kwargs)
            conn.commit()
            return result
        except (Exception, psycopg2.Error) as error:
            logger.log("Error:", error)
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()

    return wrapper


class PostgresDatabase:
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url

    @db_connection
    def execute_query(self, cursor, query: str, params: tuple = ()) -> int | None:
        try:
            cursor.execute(query, params)
            return cursor.lastrowid
        except Exception as e:
            logger.error(e)

    @db_connection
    def batch_execute_query(self, cursor, query: str, params: list[Any]):
        """
        batch_execute_query(cursor,
            "INSERT INTO test (id, v1, v2) VALUES %s",
            [(1, 2, 3), (4, 5, 6), (7, 8, 9)])

        """
        print(params)
        try:
            execute_values(cursor, query, params)

        except Exception as e:
            logger.error(e)

    @db_connection
    def create_table(self, cursor, create_table_sql: str):
        try:
            cursor.execute(create_table_sql)
        except Exception as e:
            logger.error(e)

    @db_connection
    def fetch_all(self, cursor, query: str, params: tuple = ()) -> list:
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            logger.error(e)

    @db_connection
    def fetch_one(self, cursor, query: str, params: tuple = ()) -> tuple:
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row
        except Exception as e:
            logger.error(e)

    @db_connection
    def add_column(self, cursor, table_name: str, column_definition: str):
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
        except Exception as e:
            logger.error(e)

    @db_connection
    def dangerousely_drop_table(self, cursor, table_name: str):
        try:
            cursor.execute(f"DROP TABLE {table_name}")
        except Exception as e:
            logger.error(e)
