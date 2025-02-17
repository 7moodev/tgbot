import json
import os

from backend.database.database_entity_adapter import DatabaseEntityAdapter
from backend.database.utils.db_string import convert_to_snake_case
from ..commands.utils.api.entities.token_entities import (
    TokenOverviewEntityFocus,
    convert_token_overview_to_focus
)

unique_key = ["address"]
as_array_keys = [ "price", "supply", "mc", "holder", "liquidity", "priceChange1hPercent", "circulatingSupply", "realMc"]  # fmt: skip
entity = TokenOverviewEntityFocus
tokenOverviewEntityFocusesDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

token = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"
file_path = f"backend/commands/outputs/overview/token_overview_{token}.json"
if os.path.exists(file_path):
    response = json.load(open(file_path, "r"))
    converted = convert_token_overview_to_focus(data = response["data"])

mock_data: TokenOverviewEntityFocus = converted

# Example usage
if __name__ == "__main__":
    db = tokenOverviewEntityFocusesDatabase
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data)
    # db.fetch_by_address(token)

# python -m backend.database.token_overview_entity_focuses_database
