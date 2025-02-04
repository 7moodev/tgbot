import psycopg2
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path
import json
os.environ.pop("user", None)
os.environ.pop("password", None)
os.environ.pop("host", None)
os.environ.pop("port", None)
os.environ.pop("dbname", None)
# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent / "chat" / ".env"  # Load chat .env
load_dotenv(dotenv_path=env_path)
# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

async def log_chat(chat_id, name, command, contract, full_message, reply="not passed correctly", time = 0, exc_type = None, exc_value = None, exc_traceback = None):
    if not DBNAME or not USER or not PASSWORD or not HOST or not PORT:
        print("Please set the environment")
        return  
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
        print(f"Connecting with user: {USER}")
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        print("Connection established.")
        # Example query
        insert_query = "INSERT INTO chat_logs (user_id, name, command, contract, full_message, reply, exec_time, exc_type, exc_value, exc_traceback) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (chat_id, name,command, contract, json.dumps(full_message), reply, time, exc_type, exc_value, exc_traceback)
        cursor.execute(insert_query, data)
        cursor.close()
        connection.commit()
        connection.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    try:
        print(1/0)
    except Exception as e:
        asyncio.run(log_chat(1, "test", "test", "test", "test", exc_type = type(e).__name__, exc_value = str(e), exc_traceback = str(e.__traceback__)))
    