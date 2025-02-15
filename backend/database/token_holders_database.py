import json
import os
from typing import List

from backend.database.database_entity_adapter import DatabaseEntityAdapter
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenHolderEntity,
    Mock_TokenHolderItems,
    convert_token_overview_to_focus,
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


unique_key = ["owner"]
as_array_keys = ["amount", "ui_amount"]  # fmt: skip
entity = TokenHolderEntity
tokenHoldersDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

address = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
file_path = f"top_holders.json"
if os.path.exists(file_path):
    response = json.load(open(file_path, "r"))

mock_data: TokenHolderEntity = response

# Example usage
if __name__ == "__main__":
    db = tokenHoldersDatabase
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data[0])
    # db.batch_insert(mock_data)
    # db.fetch_by_address(address)

# python -m backend.database.token_holders_database
