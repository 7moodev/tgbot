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
console = logger


class PostgresDatabase:
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url
        self.conn = None

    def connect_db(self):
        cursor = None

        try:
            result = urlparse(self.database_url)
            # print(result)
            username = result.username
            password = result.password
            database = result.path[1:]  # Remove leading slash
            hostname = result.hostname
            port = result.port

            self.conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port,
            )
            cursor = self.conn.cursor()
            self.conn.commit()
            return self.conn

        except (Exception, psycopg2.Error) as error:
            logger.log("Error:", error)
            if self.conn:
                self.conn.rollback()

    def close(self):
        self.conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> int | None:
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid
        except Exception as e:
            logger.error(e)
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()

    def batch_execute_query(self, query: str, params: list[Any]):
        """
        batch_execute_query(cursor,
            "INSERT INTO test (id, v1, v2) VALUES %s",
            [(1, 2, 3), (4, 5, 6), (7, 8, 9)])

        """
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                execute_values(cursor, query, params)

        except Exception as e:
            logger.error(e)
            raise e
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()

    def create_table(self, create_table_sql: str):
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            logger.error(e)

    def fetch_one(self, query: str, params: tuple = ()) -> tuple:
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return row
        except Exception as e:
            logger.error(e)
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()

    def add_column(self, table_name: str, column_definition: str):
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"
                )
        except Exception as e:
            logger.error(e)
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()

    def dangerousely_drop_table(self, table_name: str):
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE {table_name}")
        except Exception as e:
            logger.error(e)
        finally:
            if self.conn:
                cursor.close()
                self.conn.close()
