from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenHolderEntity,
    Mock_TokenHolderItems,
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENHOLDERDB")


class TokenHolderDatabase(PostgresDatabase):
    def __init__(self, table_name: str = "token_holders"):
        self.table_name = table_name

    def create_token_holders_table(self):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            amount TEXT,
            decimals INTEGER,
            mint TEXT,
            owner TEXT,
            token_account TEXT PRIMARY KEY,
            ui_amount INTEGER
        )
        """
        self.create_table(create_table_query)
        logger.log("Token holders table created successfully")

    def insert_token_holder(self, token_holder: TokenHolderEntity):
        insert_query = f"""
        INSERT INTO {self.table_name} (amount, decimals, mint, owner, token_account, ui_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (token_account) DO UPDATE SET
            amount = EXCLUDED.amount,
            decimals = EXCLUDED.decimals,
            mint = EXCLUDED.mint,
            owner = EXCLUDED.owner,
            ui_amount = EXCLUDED.ui_amount
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

    def batch_insert_token_holders(self, token_holders: list[TokenHolderEntity]):
        insert_query = f"""
        INSERT INTO {self.table_name} (amount, decimals, mint, owner, token_account, ui_amount)
        VALUES %s
        ON CONFLICT (token_account) DO UPDATE SET
            amount = EXCLUDED.amount,
            decimals = EXCLUDED.decimals,
            mint = EXCLUDED.mint,
            owner = EXCLUDED.owner,
            ui_amount = EXCLUDED.ui_amount
        """
        self.batch_execute_query(
            insert_query,
            token_holders,
        )
        logger.log("Batch inserted token holder data successfully")

    def fetch_all_token_holders(self):
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        logger.log("Data from token holders table:")
        for record in records:
            logger.log(record)
        return records

    def fetch_token_holder_by_account(self, token_account: str):
        fetch_query = f"SELECT * FROM {self.table_name} WHERE token_account = %s"
        record = self.fetch_one(fetch_query, (token_account,))
        logger.log(record)
        return record

    def update_token_holder(self, column_name: str, new_value, token_account: str):
        update_query = (
            f"UPDATE {self.table_name} SET {column_name} = %s WHERE token_account = %s"
        )
        self.execute_query(update_query, (new_value, token_account))
        logger.log("Token holder data updated successfully")

    def add_column(self, column_name: str, data_type: str):
        add_column_query = (
            f"ALTER TABLE {self.table_name} ADD COLUMN {column_name} {data_type}"
        )
        self.execute_query(add_column_query)
        logger.log("Column added successfully")


# Example usage
if __name__ == "__main__":
    db = TokenHolderDatabase()
    db.create_token_holders_table()
    db.batch_execute_query(Mock_TokenHolderItems)
    # Add more function calls here to test the functionality

# python -m backend.database.token_holders_database
