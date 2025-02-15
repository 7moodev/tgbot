# -------------------------------------
# token_overview_entity_focuses_database.py

import json
import os
from typing import List

import psycopg2
from backend.database.database_entity_adapter import DatabaseEntityAdapter
from backend.database.utils.db_string import convert_to_snake_case
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenOverviewEntityFocus,
    convert_token_overview_to_focus
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENOVERVIEWENTITYFOCUSDB")
console = logger

debug_should_log = False

class TokenOverviewEntityFocusesDatabase(PostgresDatabase):
    def __init__(self, as_array_keys = ['price', 'supply', 'mc', 'holder', 'liquidity', 'priceChange1hPercent', 'circulatingSupply', 'realMc']):
        super().__init__(table_name="token_overview_entity_focuses_database")
        self.as_array_keys = as_array_keys

    def create_table(self):
        self.execute_query(f"""
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
            extensions JSONB,
            logo_uri TEXT,
            timestamp TIMESTAMP[] DEFAULT ARRAY [CURRENT_TIMESTAMP]
        )
        """)
        if (debug_should_log):
            logger.log(f"{self.table_name} table created successfully")

    def insert(self, data: TokenOverviewEntityFocus):
        entries = []
        entries_as_array = []
        for item in data.items():
            if item[0] in self.as_array_keys:
                entries_as_array.append(item)
            else:
                if isinstance(item[1], dict):
                    try:
                        jsonified = psycopg2.extras.Json(item[1])
                        entries.append((item[0], jsonified))
                    except Exception as e:
                        console.error(e)
                else:
                    entries.append(item)

        columns = ', '.join([convert_to_snake_case(item[0]) for item in entries])
        if len(entries_as_array) > 0:
            columns = columns + ', ' + ', '.join([convert_to_snake_case(item[0]) for item in entries_as_array])

        placeholders = ', '.join(['%s'] * len(data))

        set_sql = ""
        on_conflict_sql = ""
        if len(self.as_array_keys) > 0:
            unique_column_name = "address"
            on_conflict_sql = f"ON CONFLICT ({unique_column_name}) DO UPDATE"
            set_sql = ",\n".join([
                f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                for item in entries_as_array
            ])
            set_sql = "SET " + set_sql + f",\ntimestamp = array_append({self.table_name}.timestamp, CURRENT_TIMESTAMP)"

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

    def batch_insert(self, data_list: list[TokenOverviewEntityFocus]):
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
                set_sql = set_sql + f", timestamp = array_append(token_overview_entity_focuses_database.timestamp, CURRENT_TIMESTAMP)"
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

    def fetch_all(self) -> List[TokenOverviewEntityFocus]:
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        if (debug_should_log):
            logger.log("Data from {self.table_name} table:")
            for record in records:
                logger.log(record)
        return records

    def fetch_by_address(self, address: str) -> TokenOverviewEntityFocus:
        fetch_query = f"SELECT * FROM {self.table_name} WHERE address = '{address}'"
        record = self.fetch_one(fetch_query)
        payload: TokenOverviewEntityFocus = {
            "id": record[0],
            "address": record[1],
            "symbol": record[2],
            "name": record[3],
            "price": record[4],
            "supply": record[5],
            "mc": record[6],
            "holder": record[7],
            "liquidity": record[8],
            "priceChange1hPercent": record[9],
            "circulatingSupply": record[10],
            "realMc": record[11],
            "extensions": record[12],
            "logoURI": record[13],
            "timestamp": record[14],
        }
        if (debug_should_log):
            logger.log(payload)

        return payload

# tokenOverviewEntityFocusesDatabase = TokenOverviewEntityFocusesDatabase()

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
