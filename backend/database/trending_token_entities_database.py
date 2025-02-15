# -------------------------------------
# trending_token_entities_database.py

from typing import List
from backend.database.database_entity_adapter import DatabaseEntityAdapter
from backend.database.utils.db_string import convert_to_snake_case
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import TrendingTokenEntity
from ..commands.utils.services.log_service import LogService

logger = LogService("TRENDINGTOKENENTITYDB")
console = logger

debug_should_log = False


class TrendingTokenEntityDatabase(PostgresDatabase):
    def __init__(
        self,
        as_array_keys=[
            "liquidity",
            "volume24hUSD",
            "volume24hChangePercent",
            "fdv",
            "marketcap",
            "rank",
            "price",
            "price24hChangePercent",
        ],
    ):
        super().__init__(table_name="trending_token_entities_database")
        self.as_array_keys = as_array_keys

    def create_table(self):
        self.execute_query(
            f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            address TEXT UNIQUE,
            decimals INTEGER,
            liquidity FLOAT[],
            logo_uri TEXT,
            name TEXT,
            symbol TEXT,
            volume24h_usd FLOAT[],
            volume24h_change_percent FLOAT[],
            fdv FLOAT[],
            marketcap FLOAT[],
            rank INTEGER[],
            price FLOAT[],
            price24h_change_percent FLOAT[],
            timestamp TIMESTAMP[] DEFAULT ARRAY [CURRENT_TIMESTAMP]
        )
        """
        )
        if debug_should_log:
            logger.log(f"{self.table_name} table created successfully")

    def insert(self, data):
        columns = ", ".join([convert_to_snake_case(key) for key in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, list(data.values()))
        if debug_should_log:
            logger.log("Inserted data successfully")

    def batch_insert(self, data_list):
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

            columns = ", ".join([convert_to_snake_case(item[0]) for item in entries])
            columns_as_array = ", ".join(
                [convert_to_snake_case(item[0]) for item in entries_as_array]
            )

            set_sql = ",\n".join(
                [
                    f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                    for item in entries_as_array
                ]
            )
            if len(self.as_array_keys):
                set_sql = (
                    set_sql
                    + f", timestamp = array_append({self.table_name}.timestamp, CURRENT_TIMESTAMP)"
                )
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

        if debug_should_log:
            logger.log("Batch inserted data successfully")

    def fetch_all(self) -> List[TrendingTokenEntity]:
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        if debug_should_log:
            logger.log("Data from {self.table_name} table:")
            for record in records:
                logger.log(record)
        return records

    def fetch_by_address(self, address: str) -> TrendingTokenEntity:
        fetch_query = f"SELECT * FROM {self.table_name} WHERE address = {address}"
        record = self.fetch_one(fetch_query)
        if debug_should_log:
            logger.log(record)
        return record

unique_key = ["address"]
as_array_keys = ["liquidity", "volume24hUSD", "volume24hChangePercent", "fdv", "marketcap", "rank", "price", "price24hChangePercent"]  # fmt: skip
entity = TrendingTokenEntity
trendingTokenEntityDatabase = DatabaseEntityAdapter(
    entity, as_array_keys=as_array_keys, unique_key=unique_key
)

# Example usage
if __name__ == "__main__":
    db = trendingTokenEntityDatabase
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(Mock_TokenOverviewItems)

# python -m backend.database.trending_token_entities_database
