import os
from postgres_database import PostgresDatabase
from commands.utils.api.entities.token_list_entity import TokenListEntity

# Initialize the PostgresDatabase with the appropriate database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bruce:@localhost:5432/Testing")
db = PostgresDatabase(DATABASE_URL)


def create_tokens_table():
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
    db.create_table(create_table_query)
    print("Tokens table created successfully")


def insert_token(token: TokenListEntity):
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
    db.execute_query(
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
    print("Inserted token data successfully")


def fetch_all_tokens():
    fetch_query = "SELECT * FROM tokens"
    records = db.fetch_all(fetch_query)
    print("Data from tokens table:")
    for record in records:
        print(record)
    return records


def fetch_token_by_address(address: str):
    fetch_query = "SELECT * FROM tokens WHERE address = %s"
    record = db.fetch_one(fetch_query, (address,))
    print(record)
    return record


def update_token(column_name: str, new_value, address: str):
    update_query = f"UPDATE tokens SET {column_name} = %s WHERE address = %s"
    db.execute_query(update_query, (new_value, address))
    print("Token data updated successfully")


def add_column(column_name: str, data_type: str):
    add_column_query = f"ALTER TABLE tokens ADD COLUMN {column_name} {data_type}"
    db.execute_query(add_column_query)
    print("Column added successfully")


# Example usage
if __name__ == "__main__":
    create_tokens_table()
    # Add more function calls here to test the functionality
