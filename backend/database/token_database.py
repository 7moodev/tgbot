from .postgres_database import PostgresDatabase
from ..commands.utils.api.entities.token_entities import TokenListEntity
from ..commands.utils.services.log_service import LogService

logger = LogService("TOKENDB")


class TokenDatabase(PostgresDatabase):
    def create_tokens_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tokens (
            address TEXT PRIMARY KEY,
            decimals INTEGER,
            price FLOAT,
            last_trade_unix_time INTEGER,
            liquidity FLOAT,
            logo_uri TEXT,
            mc FLOAT,
            name TEXT,
            symbol TEXT,
            v24h_change_percent FLOAT,
            v24h_usd FLOAT
        )
        """
        self.create_table(create_table_query)
        logger.log("Tokens table created successfully")

    def insert_token(self, token: TokenListEntity):
        insert_query = """
        INSERT INTO tokens (address, decimals, price, last_trade_unix_time, liquidity, logo_uri, mc, name, symbol, v24h_change_percent, v24h_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (address) DO UPDATE SET
            decimals = EXCLUDED.decimals,
            price = EXCLUDED.price,
            last_trade_unix_time = EXCLUDED.last_trade_unix_time,
            liquidity = EXCLUDED.liquidity,
            logo_uri = EXCLUDED.logo_uri,
            mc = EXCLUDED.mc,
            name = EXCLUDED.name,
            symbol = EXCLUDED.symbol,
            v24h_change_percent = EXCLUDED.v24h_change_percent,
            v24h_usd = EXCLUDED.v24h_usd
        """
        self.execute_query(
            insert_query,
            (
                token.address,
                token.decimals,
                token.price,
                token.lastTradeUnixTime,
                token.liquidity,
                token.logoURI,
                token.mc,
                token.name,
                token.symbol,
                token.v24hChangePercent,
                token.v24hUSD,
            ),
        )
        logger.log("Inserted token data successfully")

    def fetch_all_tokens(self):
        fetch_query = "SELECT * FROM tokens"
        records = self.fetch_all(fetch_query)
        logger.log("Data from tokens table:")
        for record in records:
            logger.log(record)
        return records

    def fetch_token_by_address(self, address: str):
        fetch_query = "SELECT * FROM tokens WHERE address = %s"
        record = self.fetch_one(fetch_query, (address,))
        logger.log(record)
        return record

    def update_token(self, column_name: str, new_value, address: str):
        update_query = f"UPDATE tokens SET {column_name} = %s WHERE address = %s"
        self.execute_query(update_query, (new_value, address))
        logger.log("Token data updated successfully")

    def add_column(self, column_name: str, data_type: str):
        add_column_query = f"ALTER TABLE tokens ADD COLUMN {column_name} {data_type}"
        self.execute_query(add_column_query)
        logger.log("Column added successfully")


# Example usage
if __name__ == "__main__":
    db = TokenDatabase()
    db.create_tokens_table()
    # Add more function calls here to test the functionality

# python -m backend.database.token_database
