# -------------------------------------
# token_overview_entities_database.py

from typing import List
from backend.database.utils.db_string import convert_to_snake_case
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import TokenOverviewEntity
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENOVERVIEWENTITYDB")
console = logger

debug_should_log = False


class TokenOverviewEntitiesDatabase(PostgresDatabase):
    def __init__(
        self,
        as_array_keys=[
            "price",
            "supply",
            "mc",
            "holder",
            "liquidity",
            "priceChange1hPercent",
            "circulatingSupply",
            "realMc",
            "logoURI",
        ],
    ):
        super().__init__(table_name="token_overview_entities_database")
        self.as_array_keys = as_array_keys

    def create_table(self):
        self.execute_query(
            f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            address TEXT UNIQUE,
            symbol TEXT,
            name TEXT,
            price FLOAT[],
            supply FLOAT[],
            mc FLOAT[],
            holder INTEGER[],
            liquidity FLOAT[],
            price_change1h_percent FLOAT[],
            circulating_supply FLOAT[],
            real_mc FLOAT[],
            extensions TEXT,
            logo_uri TEXT[],
            timestamp TIMESTAMP[] DEFAULT ARRAY [CURRENT_TIMESTAMP]
        )
        """
        )
        if debug_should_log:
            logger.log(f"{self.table_name} table created successfully")

    def insert(self, data: TokenOverviewEntity):
        entries = []
        entries_as_array = []
        for item in data.items():
            if item[0] in self.as_array_keys:
                entries_as_array.append(item)
            else:
                entries.append(item)

        columns = ", ".join([convert_to_snake_case(item[0]) for item in entries])
        if len(entries_as_array) > 0:
            columns = columns + ", ".join(
                [convert_to_snake_case(item[0]) for item in entries_as_array]
            )

        placeholders = ", ".join(["%s"] * len(data))

        set_sql = ""
        on_conflict_sql = ""
        if len(self.as_array_keys) > 0:
            unique_column_name = "token_address"
            on_conflict_sql = f"ON CONFLICT ({unique_column_name}) DO UPDATE"
            set_sql = ",\n".join(
                [
                    f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                    for item in entries_as_array
                ]
            )
            set_sql = (
                "SET "
                + set_sql
                + f", timestamp = array_append(token_creation_info_entities_database.timestamp, CURRENT_TIMESTAMP)"
            )

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
        if debug_should_log:
            logger.log("Inserted data successfully")

    def batch_insert(self, data_list: list[TokenOverviewEntity]):
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
            if len(self.as_array_keys) > 0:
                set_sql = (
                    set_sql
                    + f", timestamp = array_append(token_overview_entities_database.timestamp, CURRENT_TIMESTAMP)"
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

    def fetch_all(self) -> List[TokenOverviewEntity]:
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        if debug_should_log:
            logger.log("Data from {self.table_name} table:")
            for record in records:
                logger.log(record)
        return records

    def fetch_by_address(self, address: str) -> TokenOverviewEntity:
        fetch_query = f"SELECT * FROM {self.table_name} WHERE address = {address}"
        record = self.fetch_one(fetch_query)
        if debug_should_log:
            logger.log(record)
        return record


tokenOverviewEntitiesDatabase = TokenOverviewEntitiesDatabase()

mock_data: TokenOverviewEntity = {}

# Example usage
if __name__ == "__main__":
    db = TokenOverviewEntitiesDatabase()
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data)

# python -m backend.database.token_overview_entities_database
