# -------------------------------------
# token_creation_info_entities_database.py

from typing import List
from backend.database.database_entity_adapter import DatabaseEntityAdapter
from backend.database.utils.db_string import convert_to_snake_case
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenCreationInfoEntity
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENCREATIONINFOENTITYDB")
console = logger

debug_should_log = False

class TokenCreationInfoEntitiesDatabase(PostgresDatabase):
    def __init__(self, as_array_keys = []):
        super().__init__(table_name="token_creation_info_entities_database")
        self.as_array_keys = as_array_keys

    def create_table(self):
        self.execute_query(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            tx_hash TEXT,
            slot INTEGER,
            token_address TEXT UNIQUE,
            decimals INTEGER,
            owner TEXT,
            block_unix_time INTEGER,
            block_human_time TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        if (debug_should_log):
            logger.log(f"{self.table_name} table created successfully")

    def insert(self, data: TokenCreationInfoEntity):
        entries = []
        entries_as_array = []
        for item in data.items():
            if item[0] in self.as_array_keys:
                entries_as_array.append(item)
            else:
                entries.append(item)

        columns = ', '.join([convert_to_snake_case(item[0]) for item in entries])
        if len(entries_as_array) > 0:
            columns = columns + ', '.join([convert_to_snake_case(item[0]) for item in entries_as_array])

        placeholders = ', '.join(['%s'] * len(data))

        set_sql = ""
        on_conflict_sql = ""
        if len(self.as_array_keys) > 0:
            unique_column_name = "token_address"
            on_conflict_sql = f"ON CONFLICT ({unique_column_name}) DO UPDATE"
            set_sql = ",\n".join([
                f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                for item in entries_as_array
            ])
            set_sql = "SET " + set_sql + f", timestamp = array_append(token_creation_info_entities_database.timestamp, CURRENT_TIMESTAMP)"

        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            {on_conflict_sql}
            {set_sql}
        """

        data_values = []
        if len(entries) > 0:
            data_values = [entry[1] for entry in entries]
        if len(entries_as_array) > 0:
            data_values = data_values + [[entry[1]] for entry in entries_as_array]

        params = tuple(data_values)
        self.execute_query(query, params)
        if (debug_should_log):
            logger.log("Inserted data successfully")

    def batch_insert(self, data_list: list[TokenCreationInfoEntity]):
        if not data_list:
            return

        values = []
        for data in data_list:
            entries = []
            entries_as_array = []
            for item in data.items():
                if item[0] in self.as_array_keys:
                    entries_as_array.append(item)
                else:
                    entries.append(item)

            columns = ', '.join([convert_to_snake_case(item[0]) for item in entries])
            columns_as_array = ', '.join([convert_to_snake_case(item[0]) for item in entries_as_array])

            set_sql = ",\n".join([
                f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                for item in entries_as_array
            ])
            if len(self.as_array_keys) > 0:
                set_sql = set_sql + f", timestamp = array_append(token_creation_info_entities_database.timestamp, CURRENT_TIMESTAMP)"
            query = f"""
                INSERT INTO {self.table_name} ({columns}, {columns_as_array})
                VALUES %s
                ON CONFLICT (address) DO UPDATE
                SET {set_sql}
            """

            data_values = []
            if len(entries) > 0:
                data_values = [entry[1] for entry in entries]
            if len(entries_as_array) > 0:
                data_values = data_values + [[entry[1]] for entry in entries_as_array]
            values.append(tuple(data_values))

        self.batch_execute_query(query, values)

        if (debug_should_log):
            logger.log("Batch inserted data successfully")

    def fetch_all(self) -> List[TokenCreationInfoEntity]:
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        if (debug_should_log):
            logger.log("Data from {self.table_name} table:")
            for record in records:
                logger.log(record)
        return records

    def fetch_by_address(self, address: str) -> TokenCreationInfoEntity:
        fetch_query = f"SELECT * FROM {self.table_name} WHERE token_address = '{address}'"
        record = self.fetch_one(fetch_query)

        payload: TokenCreationInfoEntity = {
            "id": record[0],
            "txHash": record[1],
            "slot": record[2],
            "tokenAddress": record[3],
            "decimals": record[4],
            "owner": record[5],
            "blockUnixTime": record[6],
            "blockHumanTime": record[7],
            "timestamp": record[8],
        }

        if (debug_should_log):
            logger.log(payload)

        return payload

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
    db = TokenCreationInfoEntitiesDatabase()
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data)

# python -m backend.database.token_creation_info_entities_database
