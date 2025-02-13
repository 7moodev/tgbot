from backend.commands.utils.api.entities.token_entities import TrendingTokenEntity
from backend.database.utils.db_string import convert_to_snake_case, lower_first_letter, pluralize

class DatabaseGenerator:
    def __init__(self, dataclass_type, unique_key: list[str] = [], as_array_keys: list[str] = []):
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
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {{self.table_name}} (
            id SERIAL PRIMARY KEY,
            {fields_query},
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        return create_table_query

    def generate_database_service(self):
        create_table_query = self.generate_create_table_query()
        service_class_name = f"{self.dataclass_type.__name__}Database"

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

    def insert(self, data):
        columns = ', '.join([convert_to_snake_case(key) for key in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {{self.table_name}} ({{columns}}) VALUES ({{placeholders}})"
        self.execute_query(query, list(data.values()))
        if (debug_should_log):
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

            columns = ', '.join([convert_to_snake_case(item[0]) for item in entries])
            columns_as_array = ', '.join([convert_to_snake_case(item[0]) for item in entries_as_array])

            set_sql = ",\\n".join([
                f"{{convert_to_snake_case(item[0])}} = COALESCE({{self.table_name}}.{{convert_to_snake_case(item[0])}}, '{{{{}}}}') || EXCLUDED.{{convert_to_snake_case(item[0])}}"
                for item in entries_as_array
            ])
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

        console.log('>>>> _ >>>> ~ query:', query)
        console.log('>>>> _ >>>> ~ values:', values)
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
        fetch_query = f"SELECT * FROM {{self.table_name}} WHERE address = {{address}}"
        record = self.fetch_one(fetch_query)
        if (debug_should_log):
            logger.log(record)
        return record

{lower_first_letter(service_class_name)} = {service_class_name}()

# Example usage
if __name__ == "__main__":
    db = {service_class_name}()
    db.dangerousely_drop_table()
    db.create_table()
    # db.insert(Mock_TokenOverviewItems)

# python -m backend.database.{self.table_name}

    """

        return service_class_code.strip()


if __name__ == "__main__":
    # wallet_entity_service = DatabaseGenerator(WalletTokenBalanceEntity)
    as_array_keys = ["liquidity", "volume24hUSD", "volume24hChangePercent", "fdv", "marketcap", "rank", "price", "price24hChangePercent"]
    unique_key = ["address"]
    wallet_entity_service = DatabaseGenerator(TrendingTokenEntity, as_array_keys = as_array_keys, unique_key = unique_key)
    generated = wallet_entity_service.generate_database_service()
    file_name = wallet_entity_service.table_name
    with open(f"backend/database/{file_name}.py", 'w') as f:
        # write file with content
        f.write(generated)


# python -m backend.database.utils.database_generate
