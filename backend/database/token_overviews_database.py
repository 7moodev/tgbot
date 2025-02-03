from typing import List
from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import (
    TokenOverviewEntityFocus,
    Mock_TokenOverviewItems,
)
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENOVERVIEWDB")
console = logger


class TokenOverviewsDatabase(PostgresDatabase):
    def __init__(self, table_name: str = "token_overviews"):
        self.table_name = table_name
        super().__init__(table_name=table_name)

    def create_token_overviews_table(self):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            name TEXT,
            price FLOAT,
            supply FLOAT,
            mc FLOAT,
            holder INTEGER,
            liquidity FLOAT,
            priceChange1hPercent FLOAT
            circulatingSupply FLOAT,
            realMc FLOAT,
            extensions JSONB,
            logoURI TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        )
        """
        self.create_table(create_table_query)
        logger.log("Token overviews table created successfully")

    def insert_token_overview(self, token_overview: TokenOverviewEntityFocus):
        insert_query = f"""
        INSERT INTO {self.table_name} (symbol, name, price, supply, mc, holder, liquidity, circulatingSupply, priceChange1hPercent, realMc, extensions, logoURI)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.execute_query(
            insert_query,
            (
                token_overview.symbol,
                token_overview.name,
                token_overview.price,
                token_overview.supply,
                token_overview.mc,
                token_overview.holder,
                token_overview.liquidity,
                token_overview.priceChange1hPercent,
                token_overview.circulatingSupply,
                token_overview.realMc,
                token_overview.extensions,
                token_overview.logoURI,
            ),
        )
        logger.log("Inserted token overview data successfully")

    def batch_insert_token_overviews(
        self, token_overviews: List[TokenOverviewEntityFocus]
    ):
        insert_query = f"""
        INSERT INTO {self.table_name} (symbol, name, price, supply, mc, holder, liquidity, circulatingSupply, priceChange1hPercent, realMc, extensions, logoURI)
        VALUES %s
        """
        params = [
            (
                to.symbol,
                to.name,
                to.price,
                to.supply,
                to.mc,
                to.holder,
                to.liquidity,
                to.priceChange1hPercent,
                to.circulatingSupply,
                to.realMc,
                to.extensions,
                to.logoURI,
            )
            for to in token_overviews
        ]
        self.batch_execute_query(
            insert_query,
            params,
        )
        logger.log("Batch inserted token overview data successfully")

    def fetch_all_token_overviews(self):
        fetch_query = f"SELECT * FROM {self.table_name}"
        records = self.fetch_all(fetch_query)
        logger.log("Data from token overviews table:")
        for record in records:
            logger.log(record)
        return records


tokenOverviewsDatabase = TokenOverviewsDatabase()

# Example usage
if __name__ == "__main__":
    db = TokenOverviewsDatabase()
    # db.dangerousely_drop_table()
    db.create_token_overviews_table()
    db.batch_insert_token_overviews(Mock_TokenOverviewItems)
    # Add more function calls here to test the functionality

# python -m backend.database.token_overviews_database
