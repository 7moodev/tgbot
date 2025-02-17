from backend.database.database_entity_adapter import DatabaseEntityAdapter
from backend.database.utils.db_string import convert_to_snake_case
from ..commands.utils.api.entities.token_entities import TrendingTokenEntity

unique_key = ["address"]
as_array_keys = ["liquidity", "volume24hUSD", "volume24hChangePercent", "fdv", "marketcap", "rank", "price", "price24hChangePercent"]  # fmt: skip
entity = TrendingTokenEntity
trendingTokenEntityDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

# Example usage
if __name__ == "__main__":
    db = trendingTokenEntityDatabase
    # db.dangerousely_drop_table()
    # db.create_table()
    # fetched = db.fetch_by_address("6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN")
    fetched = db.fetch_all()
    # db.insert(Mock_TokenOverviewItems)

# python -m backend.database.trending_token_entities_database
