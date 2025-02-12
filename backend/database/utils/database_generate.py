import re
from ...commands.utils.api.entities.wallet_entities import (
    WalletEntity,
    WalletTokenBalanceEntity,
)


def camel_to_snake(name):
    """Convert camelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def convert_to_snake_case(content):
    """Convert all camelCase identifiers in the Python script to snake_case."""

    def replace_match(match):
        word = match.group()
        return camel_to_snake(word)

    # Match variable, function, and argument names (but avoid string contents and comments)
    pattern = re.compile(r"\b[a-zA-Z][a-zA-Z0-9]*\b")
    return pattern.sub(replace_match, content)


def pluralize(noun):
    """Convert a singular noun to its plural form."""
    if re.search("[sxz]$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[^aeioudgkprt]h$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[aeiou]y$", noun):
        return re.sub("y$", "ys", noun)
    elif re.search("[^aeiou]y$", noun):
        return re.sub("y$", "ies", noun)
    else:
        return noun + "s"


class DatabaseGenerator:
    def __init__(self, dataclass_type):
        self.dataclass_type = dataclass_type
        plural = pluralize(dataclass_type.__name__)
        name = convert_to_snake_case(plural)
        table_name = f"{name}_database"
        self.table_name = table_name

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
            fields.append(f"{field_name} {sql_type}")
        fields_query = ",\n            ".join(fields)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            {fields_query}
        )
        """
        return create_table_query

    def generate_database_service(self):
        create_table_query = self.generate_create_table_query()
        service_class_name = f"{self.dataclass_type.__name__}Database"

        service_class_code = f"""
-------------------------------------
{self.table_name}.py

from typing import List
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
)
from ..commands.utils.services.log_service import LogService

logger = LogService("{self.dataclass_type.__name__.upper()}DB")
console = logger

class {service_class_name}(PostgresDatabase):
    def __init__(self):
        super().__init__(table_name="{self.table_name}")

    def create_table(self):
        self.execute_query(\"\"\"{create_table_query}\"\"\")
        logger.log("{self.table_name} table created successfully")

    def insert(self, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({{columns}}) VALUES ({{placeholders}})"
        self.execute_query(query, list(data.values()))
        logger.log("Inserted data successfully")

    def batch_insert(self, data_list):
        if not data_list:
            return
        columns = ', '.join(data_list[0].keys())
        query = f"INSERT INTO {self.table_name} ({{columns}}) VALUES %s"
        values = [list(data.values()) for data in data_list]
        self.batch_execute_query(query, values)
        logger.log("Batch inserted data successfully")

{service_class_name} = {service_class_name}()

# Example usage
if __name__ == "__main__":
    db = {service_class_name}()
    # db.dangerousely_drop_table()
    db.create_table()
    # db.insert(Mock_TokenOverviewItems)

# python -m backend.database.{self.table_name}

    """

        return service_class_code.strip()


if __name__ == "__main__":
    wallet_entity_service = DatabaseGenerator(WalletTokenBalanceEntity)
    generated = wallet_entity_service.generate_database_service()
    print(">>>> _ >>>> ~ generated:", generated)

# python -m tgbot.backend.database.utils.database_generate
