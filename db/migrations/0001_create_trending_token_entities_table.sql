
CREATE TABLE IF NOT EXISTS token_creation_info_entities_database (
    id SERIAL PRIMARY KEY,
    tx_hash TEXT,
    slot INTEGER,
    token_address TEXT UNIQUE,
    decimals INTEGER,
    owner TEXT,
    block_unix_time INTEGER,
    block_human_time TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

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

CREATE TABLE IF NOT EXISTS token_holders (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount TEXT,
    decimals INTEGER,
    mint TEXT,
    owner TEXT,
    token_account TEXT,
    ui_amount INTEGER
)

CREATE TABLE IF NOT EXISTS token_overview_entity_focuses_database (
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

CREATE TABLE IF NOT EXISTS trending_token_entities_database (
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
);

CREATE TABLE IF NOT EXISTS user_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    user_id TEXT,
    coin_address TEXT,
    command_name TEXT,
    command_result,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE IF NOT EXISTS wallet_token_balance_entities_database (
    id SERIAL PRIMARY KEY,
    uiAmount FLOAT,
    priceUsd FLOAT,
    valueUsd FLOAT,
    address TEXT,
    name TEXT,
    symbol TEXT,
    decimals INTEGER,
    balance TEXT,
    chainId TEXT
)
