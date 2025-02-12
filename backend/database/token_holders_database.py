from typing import List
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenHolderEntity,
    Mock_TokenHolderItems,
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENHOLDERDB")
console = logger


class TokenHoldersDatabase(PostgresDatabase):
    def __init__(self, table_name: str = "token_holders"):
        self.table_name = table_name
        super().__init__(table_name=table_name)

    def create_token_holders_table(self):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount TEXT,
            decimals INTEGER,
            mint TEXT,
            owner TEXT,
            token_account TEXT,
            ui_amount INTEGER
        )
        """
        self.create_table(create_table_query)
        logger.log("Token holders table created successfully")

    def insert_token_holder(self, token_holder: TokenHolderEntity):
        insert_query = f"""
        INSERT INTO {self.table_name} (amount, decimals, mint, owner, token_account, ui_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute_query(
            insert_query,
            (
                token_holder.amount,
                token_holder.decimals,
                token_holder.mint,
                token_holder.owner,
                token_holder.token_account,
                token_holder.ui_amount,
            ),
        )
        logger.log("Inserted token holder data successfully")

    def batch_insert_token_holders(self, token_holders: List[TokenHolderEntity]):
        insert_query = f"""
        INSERT INTO {self.table_name} (amount, decimals, mint, owner, token_account, ui_amount)
        VALUES %s
        """
        params = [
            (
                th["amount"],
                th["decimals"],
                th["mint"],
                th["owner"],
                th["token_account"],
                th["ui_amount"],
            )
            for th in token_holders
        ]
        self.batch_execute_query(
            insert_query,
            params,
        )
        logger.log("Batch inserted token holder data successfully")

    def fetch_all_token_holders(self):
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        logger.log("Data from token holders table:")
        for record in records:
            logger.log(record)
        return records


tokenHoldersDatabase = TokenHoldersDatabase()

# Example usage
if __name__ == "__main__":
    db = TokenHoldersDatabase()
    # db.dangerousely_drop_table()
    db.create_token_holders_table()
    db.batch_insert_token_holders(Mock_TokenHolderItems)
    # Add more function calls here to test the functionality

# python -m backend.database.token_holders_database
