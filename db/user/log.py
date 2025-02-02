import psycopg2
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path
os.environ.pop("user", None)
os.environ.pop("password", None)
os.environ.pop("host", None)
os.environ.pop("port", None)
os.environ.pop("dbname", None)
# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent / "user" / ".env"  # Load chat .env
load_dotenv(dotenv_path=env_path)
# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
# Connect to the database
log_data = {}
def set_log_data(key, value):
    log_data[key] = value
    if 'pubkey' in log_data and 'private' in log_data:
       log_user((log_data.get('user_id'), -1), log_data.get('name', 'pew'), log_data['pubkey'], log_data['private'], log_data.get('valid_until', '-1'))
    log_data.clear()
def log_user(user_id, name, pubkey, private):
    if not DBNAME or not USER or not PASSWORD or not HOST or not PORT:
        print("Please set the environment variables.")
        return
    if not name:
        name = 'pew'
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            sslmode="require",       # Use SSL as required by Supabase
            gssencmode="disable",    # Disable GSSAPI encryption
            connect_timeout=10  
        )
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        # Example query
        insert_query = "INSERT INTO userbase (user_id, name, pubkey, private) VALUES (%s, %s, %s, %s);"
        data = (user_id,name, pubkey, private)
        cursor.execute(insert_query, data)
        cursor.close()
        connection.commit()
        connection.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Failed to connect: {e}")
#print(log_user(123456, "Tesot", "Teddadadst", "Test"))
