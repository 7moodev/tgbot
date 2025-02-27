from typing import Any
import psycopg2
from backend.commands.utils.api.entities.token_entities import (
    TokenCreationInfoEntity,
    TokenOverviewEntityFocus,
    TrendingTokenEntity,
)
from backend.commands.utils.services.log_service import LogService
from backend.database.postgres_database import PostgresDatabase
from backend.database.utils.db_string import (
    convert_to_snake_case,
    lower_first_letter,
    pluralize,
)

logger = LogService("DBADAPTER")
console = logger

debug_should_log = False

class DatabaseEntityAdapter(PostgresDatabase):
    def __init__(
        self,
        dataclass_type,
        unique_key: list[str] = ["address"],
        as_array_keys: list[str] = [],
    ):
        self.dataclass_type = dataclass_type
        self.table_name = self.get_table_name(dataclass_type)
        self.unique_key = unique_key
        self.as_array_keys = as_array_keys
        super().__init__(table_name=self.table_name)

    def get_table_name(self, dataclass_type) -> str:
        plural = pluralize(dataclass_type.__name__)
        name = convert_to_snake_case(plural)
        table_name = f"{name}_database"
        return table_name

    def python_type_to_sql(self, python_type):
        type_mapping = {
            str: "TEXT",
            int: "INTEGER",
            float: "FLOAT",
            bool: "BOOLEAN",
            list: "JSONB",
            dict: "JSONB",
        }
        return type_mapping.get(python_type, "TEXT")

    def generate_create_table_query(self):
        fields = []
        for field in self.dataclass_type.__dataclass_fields__.items():
            field_name, field_info = field
            sql_type = self.python_type_to_sql(field_info.type)
            if field_name in self.unique_key:
                sql_type = sql_type + " UNIQUE"
            if field_name in self.as_array_keys:
                sql_type = sql_type + "[]"
            fields.append(f"{convert_to_snake_case(field_name)} {sql_type}")
        fields_query = ",\n            ".join(fields)
        sql_timestamp = "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        if len(self.as_array_keys) > 0:
            sql_timestamp = "timestamp TIMESTAMP[] DEFAULT ARRAY [CURRENT_TIMESTAMP]"

        created = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            {fields_query},
            {sql_timestamp}
        )
        """
        return created

    def generate_fetch_one_payload(self, record: tuple) -> str:
        field_assignments = []
        for field_name, field_info in self.dataclass_type.__dataclass_fields__.items():
            key_list = list(self.dataclass_type.__dataclass_fields__.keys())
            field_assignments.append(f"\"{field_name}\": record[{key_list.index(field_name) + 1}]")

        payload = {
            "id": record[0],
            **{field_name: record[key_list.index(field_name) + 1][-1] if isinstance(record[key_list.index(field_name) + 1], list) else record[key_list.index(field_name) + 1] for field_name in self.dataclass_type.__dataclass_fields__.keys() },
            "timestamp": record[len(self.dataclass_type.__dataclass_fields__) + 1],
        }
        return payload


    def generate_database_service(self):
        create_table_query = self.generate_create_table_query()
        service_class_name = f"{pluralize(self.dataclass_type.__name__)}Database"

        service_class_code = f"""
# -------------------------------------
# {self.table_name}.py

from typing import List

import psycopg2
from backend.database.utils.db_string import convert_to_snake_case
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    {self.dataclass_type.__name__}
)
from ..commands.utils.services.log_service import LogService

logger = LogService("{self.dataclass_type.__name__.upper()}DB")
console = logger

debug_should_log = False

class {service_class_name}(PostgresDatabase):
    def __init__(self, as_array_keys = {self.as_array_keys}):
        super().__init__(table_name="{self.table_name}")
        self.as_array_keys = as_array_keys





{lower_first_letter(service_class_name)} = {service_class_name}()

mock_data: {self.dataclass_type.__name__} = {{

}}

# Example usage
if __name__ == "__main__":
    db = {service_class_name}()
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(mock_data)

# python -m backend.database.{self.table_name}

    """

        return service_class_code.strip()

    def create_table(self):
        create_table_query = self.generate_create_table_query()
        self.execute_query(f"""{create_table_query}""")

        if (debug_should_log):
            logger.log(f"{self.table_name} table created successfully")

    def insert(self, data: TokenOverviewEntityFocus):
        entries = []
        entries_as_array = []
        if data == None:
            return
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
        if len(self.unique_key) > 0:
            on_conflict_sql = f"ON CONFLICT ({convert_to_snake_case(self.unique_key[0])}) DO NOTHING"
        if len(self.as_array_keys) > 0:
            on_conflict_sql = f"ON CONFLICT ({convert_to_snake_case(self.unique_key[0])}) DO UPDATE"
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

    def ensure_missing_field_is_null(self, data: dict):
        """
        Ensure that all fields are present in the data dictionary, because
        Bug: Endpoint returns data with missing fields
        """
        for field in self.dataclass_type.__dataclass_fields__.keys():
            if field not in data:
                data[field] = None
        # ensure fields are in the correct order
        ordered = {k: data[k] for k in self.dataclass_type.__dataclass_fields__.keys()}
        return ordered

    def batch_insert(self, data_list: list[Any]):
        if not data_list:
            return

        values = []
        expected_num_of_fields = len(self.dataclass_type.__dataclass_fields__.items())
        for data in data_list:
            if not len(data.items()) == expected_num_of_fields:
                data = self.ensure_missing_field_is_null(data)

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

            set_sql = ""
            on_conflict_sql = ""
            if len(self.as_array_keys) > 0:
                on_conflict_sql = f"ON CONFLICT ({self.unique_key[0]}) DO UPDATE"
                set_sql = ",\n".join([
                    f"{convert_to_snake_case(item[0])} = COALESCE({self.table_name}.{convert_to_snake_case(item[0])}, '{{}}') || EXCLUDED.{convert_to_snake_case(item[0])}"
                    for item in entries_as_array
                ])
                set_sql = "SET " + set_sql + f",\ntimestamp = array_append({self.table_name}.timestamp, CURRENT_TIMESTAMP)"

            query = f"""
                INSERT INTO {self.table_name} ({columns})
                VALUES %s
                {on_conflict_sql}
                {set_sql}
            """

            data_values = []
            if len(entries) > 0:
                data_values = [entry[1] for entry in entries]
            if len(entries_as_array) > 0:
                data_values = data_values + [[entry[1]] for entry in entries_as_array]
            values.append(tuple(data_values))

        for i in range(0, len(values), 10):
            self.batch_execute_query(query, values[i:i + 10])

        if (debug_should_log):
            logger.log("Batch inserted data successfully")

    def fetch_all(self) -> list[Any]:
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = super().fetch_all(fetch_query)
        if (debug_should_log):
            logger.log(f"Data from {self.table_name} table:")
            for record in records:
                logger.log(record)
        payload = [self.generate_fetch_one_payload(record) for record in records]
        return payload

    def fetch_by_address(self, address: str):
        fetch_query = f"SELECT * FROM {self.table_name} WHERE {convert_to_snake_case(self.unique_key[0])} = '{address}'"
        record = self.fetch_one(fetch_query)
        payload = self.generate_fetch_one_payload(record)
        if (debug_should_log):
            logger.log(payload)

        return payload


if __name__ == "__main__":
    # wallet_entity_service = DatabaseGenerator(WalletTokenBalanceEntity)

    unique_key = ["address"]
    as_array_keys = [ "price", "supply", "mc", "holder", "liquidity", "priceChange1hPercent", "circulatingSupply", "realMc"]  # fmt: skip
    entity = TokenOverviewEntityFocus
    # unique_key = ["tokenAddress"]
    # as_array_keys = []
    # entity = TokenCreationInfoEntity
    # as_array_keys = ["liquidity", "volume24hUSD", "volume24hChangePercent", "fdv", "marketcap", "rank", "price", "price24hChangePercent"]  # fmt: skip
    # entity = TrendingTokenEntity

    wallet_entity_service = DatabaseEntityAdapter(
        entity, as_array_keys=as_array_keys, unique_key=unique_key
    )
    generated = wallet_entity_service.generate_database_service()


# python -m backend.database.utils.database_entity_adapter
