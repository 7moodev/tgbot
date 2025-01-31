import sqlite3
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = ()) -> int | None:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def create_table(self, create_table_sql: str):
        self.execute_query(create_table_sql)

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows

    def fetch_one(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        with self.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row

    def add_column(self, table_name: str, column_definition: str):
        self.execute_query(f'ALTER TABLE {table_name} ADD COLUMN {column_definition}')

    def dangerousely_drop_table(self, table_name):
      self.execute_query(f'DROP TABLE IF EXISTS {table_name}')

