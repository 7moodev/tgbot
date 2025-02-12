import json
from typing import List, Dict, Any
from .sqlite_database import SqliteDatabase
from ..commands.utils.constants import DB_REL_PATH_TAMAGO

DATABASE_PATH = DB_REL_PATH_TAMAGO
TABLE_NAME = "user_logs"


class UserLogsDatabase(SqliteDatabase):
    def __init__(self, db_path: str = DATABASE_PATH):
        super().__init__(db_path)
        self.create_table()

    def create_table(self):
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                user_id TEXT,
                coin_address TEXT,
                command_name TEXT,
                command_result,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        super().create_table(create_table_sql)

    def insert_log(
        self,
        username: str,
        user_id: str,
        coin_address: str,
        command_name: str,
        command_result: str = None,
    ) -> int | None:
        last_row_id = self.execute_query(
            f"""
            INSERT INTO {TABLE_NAME} (username, user_id, coin_address, command_name, command_result)
            VALUES (?, ?, ?, ?, ?)
        """,
            (username, user_id, coin_address, command_name, command_result),
        )
        return last_row_id

    def fetch_all_logs(self) -> List[Dict[str, Any]]:
        rows = self.fetch_all(f"SELECT * FROM {TABLE_NAME}")
        return "\n".join(
            [
                str(
                    dict(
                        id=row[0],
                        username=row[1],
                        user_id=row[2],
                        coin_address=row[3],
                        command_name=row[4],
                        command_result=row[5],
                        timestamp=row[6],
                    )
                )
                for row in rows
            ]
        )

    def fetch_log_by_id(self, log_id: int) -> Dict[str, Any]:
        row = self.fetch_one(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (log_id,))
        if row:
            return dict(
                id=row[0],
                username=row[1],
                coin_address=row[2],
                command_name=row[3],
                command_result=row[4],
                timestamp=row[5],
            )
        return None

    def fetch_by(self, property: str, value):
        rows = self.fetch_all(
            f"SELECT * FROM {TABLE_NAME} WHERE {property} = ?", (value,)
        )
        return [
            dict(
                id=row[0],
                username=row[1],
                coin_address=row[2],
                command_name=row[3],
                command_result=row[4],
                timestamp=row[5],
            )
            for row in rows
        ]

    def fetch_log_by_username(self, value: str):
        self.fetch_by("username", value)

    def fetch_log_by_user_id(self, value: str):
        self.fetch_by("user_id", value)

    def fetch_log_by_coin_address(self, value: str):
        self.fetch_by("coin_address", value)

    def update_log(
        self,
        log_id: int,
        username: str,
        coin_address: str,
        command_name: str,
        command_result: str = None,
    ):
        self.execute_query(
            f"""
            UPDATE {TABLE_NAME}
            SET username = ?, coin_address = ?, command_name = ?, command_result = ?
            WHERE id = ?
        """,
            (username, coin_address, command_name, command_result, log_id),
        )

    def update_logs_called_mapping(self, command_name: str, user_id: str):
        # "TODO: add `command_called` column"
        if 1:
            return

        row = self.fetch_one(
            f"SELECT command_called FROM {TABLE_NAME} WHERE user_id = {user_id}"
        )
        if row:
            command_called = json.loads(row[0]) if row[0] else {}
        else:
            command_called = {}

        # Increment the count for the specified command
        if command_name in command_called:
            command_called[command_name] += 1
        else:
            command_called[command_name] = 1

        # Convert the dictionary back to a JSON string
        command_called_str = json.dumps(command_called)

        # Update the database with the new command_called value
        self.execute_query(
            f"""
            UPDATE {TABLE_NAME}
            SET command_called = ?
            WHERE id = {user_id}
        """,
            (command_called_str,),
        )

    def delete_log(self, log_id: int):
        self.execute_query("DELETE FROM ${TABLE_NAME} WHERE id = ?", (log_id,))


# Example usage
if __name__ == "__main__":
    db = UserLogsDatabase()
    # db.dangerousely_drop_table(TABLE_NAME)  # This will drop the user_logs table
    # db.add_column(TABLE_NAME, 'user_id TEXT')  # This will add a new column to the user_logs table

    db.create_table()  # This will recreate the user_logs table
    db.insert_log("user1", "id1", "address1", "command1", "result1")
    # db.update_logs_called_mapping('/test', '1')  # Increment the count for the 'test' command
    logs = db.fetch_all_logs()
    print(logs)

# "python -m backend.database.user_logs_database"
