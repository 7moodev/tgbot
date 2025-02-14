from backend.commands.utils.api.entities.token_entities import (
    TokenCreationInfoEntity,
    TokenOverviewEntityFocus,
    TrendingTokenEntity,
)
from backend.database.utils.db_string import (
    convert_to_snake_case,
    lower_first_letter,
    pluralize,
)


class DatabaseGenerator:
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
            list: "JSONB",  # Assuming lists will be stored as JSON
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

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {{self.table_name}} (
            id SERIAL PRIMARY KEY,
            {fields_query},
            {sql_timestamp}
        )
        """
        return create_table_query

    def generate_fetch_one_entity(self) -> str:
        field_assignments = []
        for field_name, field_info in self.dataclass_type.__dataclass_fields__.items():
            field_assignments.append(f"{field_name}=record[{list(self.dataclass_type.__dataclass_fields__.keys()).index(field_name) + 1}]")
        field_assignments_str = ",\n            ".join(field_assignments)

        return f"""
        payload = {self.dataclass_type.__name__}(
            {field_assignments_str}
        )
        """


    def generate_database_service(self):
        create_table_query = self.generate_create_table_query()
        service_class_name = f"{pluralize(self.dataclass_type.__name__)}Database"

        service_class_code = f"""
# -------------------------------------
# {self.table_name}.py

from typing import List
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

    def create_table(self):
        self.execute_query(f\"\"\"{create_table_query}\"\"\")
        if (debug_should_log):
            logger.log(f"{{self.table_name}} table created successfully")

    def insert(self, data: {self.dataclass_type.__name__}):
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
            on_conflict_sql = f"ON CONFLICT ({{unique_column_name}}) DO UPDATE"
            set_sql = ",\\n".join([
                f"{{convert_to_snake_case(item[0])}} = COALESCE({{self.table_name}}.{{convert_to_snake_case(item[0])}}, '{{{{}}}}') || EXCLUDED.{{convert_to_snake_case(item[0])}}"
                for item in entries_as_array
            ])
            set_sql = "SET " + set_sql + f", timestamp = array_append(token_creation_info_entities_database.timestamp, CURRENT_TIMESTAMP)"

        query = f\"\"\"
            INSERT INTO {{self.table_name}} ({{columns}})
            VALUES ({{placeholders}})
            {{on_conflict_sql}}
            {{set_sql}}
        \"\"\"

        data_values = []
        if len(entries) > 0:
            data_values = [entry[1] for entry in entries]
        if len(entries_as_array) > 0:
            data_values = data_values + [[entry[1]] for entry in entries_as_array]

        params = tuple(data_values)
        self.execute_query(query, params)
        if (debug_should_log):
            logger.log("Inserted data successfully")

    def batch_insert(self, data_list: list[{self.dataclass_type.__name__}]):
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

            set_sql = ",\\n".join([
                f"{{convert_to_snake_case(item[0])}} = COALESCE({{self.table_name}}.{{convert_to_snake_case(item[0])}}, '{{{{}}}}') || EXCLUDED.{{convert_to_snake_case(item[0])}}"
                for item in entries_as_array
            ])
            if len(self.as_array_keys) > 0:
                set_sql = set_sql + f", timestamp = array_append({self.table_name}.timestamp, CURRENT_TIMESTAMP)"
            query = f\"""
                INSERT INTO {{self.table_name}} ({{columns}}, {{columns_as_array}})
                VALUES %s
                ON CONFLICT (address) DO UPDATE
                SET {{set_sql}}
            \"""

            data_values = []
            if len(entries) > 0:
                data_values = [entry[1] for entry in entries]
            if len(entries_as_array) > 0:
                data_values = data_values + [[entry[1]] for entry in entries_as_array]
            values.append(tuple(data_values))

        self.batch_execute_query(query, values)

        if (debug_should_log):
            logger.log("Batch inserted data successfully")

    def fetch_all(self) -> List[{self.dataclass_type.__name__}]:
        fetch_query = f"SELECT * FROM {{self.table_name}}"
        records = self.fetch_all(fetch_query)
        if (debug_should_log):
            logger.log("Data from {{self.table_name}} table:")
            for record in records:
                logger.log(record)
        return records

    def fetch_by_address(self, address: str) -> {self.dataclass_type.__name__}:
        fetch_query = f"SELECT * FROM {{self.table_name}} WHERE {convert_to_snake_case(self.unique_key[0])} = '{{address}}'"
        record = self.fetch_one(fetch_query)
        {self.generate_fetch_one_entity()}
        if (debug_should_log):
            logger.log(payload)

        return payload

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


if __name__ == "__main__":
    # wallet_entity_service = DatabaseGenerator(WalletTokenBalanceEntity)
    # unique_key = ["address"]
    # as_array_keys = [ "price", "supply", "mc", "holder", "liquidity", "priceChange1hPercent", "circulatingSupply", "realMc", "logoURI" ]  # fmt: skip
    # entity = TokenOverviewEntityFocus
    unique_key = ["tokenAddress"]
    as_array_keys = []
    entity = TokenCreationInfoEntity
    # as_array_keys = ["liquidity", "volume24hUSD", "volume24hChangePercent", "fdv", "marketcap", "rank", "price", "price24hChangePercent"]  # fmt: skip
    # entity = TrendingTokenEntity

    wallet_entity_service = DatabaseGenerator(
        entity, as_array_keys=as_array_keys, unique_key=unique_key
    )
    generated = wallet_entity_service.generate_database_service()
    file_name = wallet_entity_service.table_name
    with open(f"backend/database/{file_name}.py", "w") as f:
        f.write(generated)


# python -m backend.database.utils.database_generate
