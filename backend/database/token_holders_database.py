import json
import os

from backend.database.database_entity_adapter import DatabaseEntityAdapter
from ..commands.utils.api.entities.token_entities import (
    TokenHolderEntity,
    Mock_TokenHolderItems,
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENHOLDERDB")
console = logger


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
