from backend.database.database_entity_adapter import DatabaseEntityAdapter
from ..commands.utils.api.entities.token_entities import TokenListEntity

unique_key = ["tokenAddress"]
as_array_keys = []
entity = TokenListEntity
tokensDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

mock_data: TokenListEntity = {

}

# Example usage
if __name__ == "__main__":
    db = tokensDatabase()
    db.create_tokens_table()
    # Add more function calls here to test the functionality

# python -m backend.database.token_database
