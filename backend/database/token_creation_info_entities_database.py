from backend.database.database_entity_adapter import DatabaseEntityAdapter
from ..commands.utils.api.entities.token_entities import (
    TokenCreationInfoEntity
)

unique_key = ["tokenAddress"]
as_array_keys = []
entity = TokenCreationInfoEntity
tokenCreationInfoEntitiesDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

mock_data: TokenCreationInfoEntity = {

}

# Example usage
if __name__ == "__main__":
    db = tokenCreationInfoEntitiesDatabase()
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data)

# python -m backend.database.token_creation_info_entities_database
