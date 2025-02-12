from typing import List
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.wallet_entities import Mock_WalletTokenBalanceEntity
from ..commands.utils.services.log_service import LogService

logger = LogService("WALLETTOKENBALANCEENTITYDB")
console = logger


class WalletTokenBalanceEntityDatabase(PostgresDatabase):
    def __init__(self):
        super().__init__(table_name="wallet_token_balance_entities_database")

    def create_table(self):
        self.execute_query(
            """
        CREATE TABLE IF NOT EXISTS wallet_token_balance_entities_database (
            id SERIAL PRIMARY KEY,
            uiAmount FLOAT,
            priceUsd FLOAT,
            valueUsd FLOAT,
            address TEXT,
            name TEXT,
            symbol TEXT,
            decimals INTEGER,
            balance TEXT,
            chainId TEXT
        )
        """
        )
        logger.log("wallet_token_balance_entities_database table created successfully")

    def insert(self, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO wallet_token_balance_entities_database ({columns}) VALUES ({placeholders})"
        self.execute_query(query, list(data.values()))
        logger.log("Inserted data successfully")

    def batch_insert(self, data_list):
        if not data_list:
            return
        columns = ", ".join(data_list[0].keys())
        query = (
            f"INSERT INTO wallet_token_balance_entities_database ({columns}) VALUES %s"
        )
        values = [list(data.values()) for data in data_list]
        self.batch_execute_query(query, values)
        logger.log("Batch inserted data successfully")


walletTokenBalanceEntityDatabase = WalletTokenBalanceEntityDatabase()

# Example usage
if __name__ == "__main__":
    db = WalletTokenBalanceEntityDatabase()
    # db.dangerousely_drop_table()
    db.create_table()
    db.insert(Mock_WalletTokenBalanceEntity)

# python -m backend.database.wallet_token_balance_entities_database
