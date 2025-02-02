import os
import psycopg2
from urllib.parse import urlparse

from ..commands.utils.services.log_service import LogService

# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://bruce:@localhost:5432/Testing')
DATABASE_URL = os.getenv("DATABASE_URL")


logger = LogService("POSTGRES")


class PostgresDatabase:
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url

    def connect_db(self):
        cursor = None

        try:
            result = urlparse(self.database_url)
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
            conn.commit()
            return conn

        except (Exception, psycopg2.Error) as error:
            logger.log("Error:", error)
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
                logger.log("PostgreSQL connection is closed")

    def execute_query(self, query: str, params: tuple = ()) -> int | None:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def create_table(self, create_table_sql: str):
        self.execute_query(create_table_sql)

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows

    def fetch_one(self, query: str, params: tuple = ()) -> tuple:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row

    def add_column(self, table_name: str, column_definition: str):
        self.execute_query(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
