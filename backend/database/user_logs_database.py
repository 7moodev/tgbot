from typing import List, Dict, Any
from .database import Database
from ..commands.utils.constants import DB_REL_PATH_TAMAGO
from .database_entity import UserLogEntity

# Creating an instance
log_entry = UserLogEntity(
    id=1,
    username="user123",
    coin_address="0xABC123...",
    command_name="check_balance",
    command_result="Balance: 100 tokens",
    timestamp="2025-01-30 12:34:56"
)

DATABASE_PATH = DB_REL_PATH_TAMAGO

class UserLogsDatabase(Database):
    def __init__(self, db_path: str = DATABASE_PATH):
      super().__init__(db_path)
      self.create_table()

    def create_table(self):
        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                coin_address TEXT NOT NULL,
                command_name TEXT NOT NULL,
                command_result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        super().create_table(create_table_sql)

    def insert_log(self, username: str, coin_address: str, command_name: str, command_result: str = None):
        self.execute_query('''
            INSERT INTO user_logs (username, coin_address, command_name, command_result)
            VALUES (?, ?, ?, ?)
        ''', (username, coin_address, command_name, command_result))

    def fetch_all_logs(self) -> List[Dict[str, Any]]:
        rows = self.fetch_all('SELECT * FROM user_logs')
        return [dict(id=row[0], username=row[1], coin_address=row[2], command_name=row[3], command_result=row[4], timestamp=row[5]) for row in rows]

    def fetch_log_by_id(self, log_id: int) -> Dict[str, Any]:
        row = self.fetch_one('SELECT * FROM user_logs WHERE id = ?', (log_id,))
        if row:
            return dict(id=row[0], username=row[1], coin_address=row[2], command_name=row[3], command_result=row[4], timestamp=row[5])
        return None

    def fetch_by(self, property: str, value):
        rows = self.fetch_all(f'SELECT * FROM user_logs WHERE {property} = ?', (value,))
        return [dict(id=row[0], username=row[1], coin_address=row[2], command_name=row[3], command_result=row[4], timestamp=row[5]) for row in rows]

    def fetch_log_by_username(self, value: str):
      self.fetch_by('username', value)

    def fetch_log_by_coin_address(self, value: str):
      self.fetch_by('coin_address', value)

    def update_log(self, log_id: int, username: str, coin_address: str, command_name: str, command_result: str = None):
        self.execute_query('''
            UPDATE user_logs
            SET username = ?, coin_address = ?, command_name = ?, command_result = ?
            WHERE id = ?
        ''', (username, coin_address, command_name, command_result, log_id))

    def delete_log(self, log_id: int):
        self.execute_query('DELETE FROM user_logs WHERE id = ?', (log_id,))

# Example usage
if __name__ == "__main__":
    db = UserLogsDatabase()
    db.dangerousely_drop_table("user_logs")  # This will drop the user_logs table
    db.create_table()  # This will recreate the user_logs table
    db.insert_log('user1', 'address1', 'command1', 'result1')
    logs = db.fetch_all_logs()
    print(logs)

# python -m backend.database.user_log_database
