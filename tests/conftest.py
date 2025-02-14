import os
from dotenv import load_dotenv
import psycopg2
import pytest
import sys

load_dotenv()

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, root_path)

TEST_DB_URL = os.getenv("DATABASE_URL")
TEST_DB_NAME = "unit_tests"


@pytest.fixture
def test_db():
    # Ensure a separate connection for database management
    conn = psycopg2.connect(TEST_DB_URL)
    conn.set_session(autocommit=True)  # Set autocommit explicitly
    cur = conn.cursor()

    # Drop & recreate the test database
    cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
    cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    cur.close()
    conn.close()

    # Return a connection to the newly created test database
    test_db_conn = psycopg2.connect(
        TEST_DB_URL.replace("dbname=", f"dbname={TEST_DB_NAME}")
    )
    print("here <<<<<<<<<<<<<<<<<<<<<")
    print(f"dbname={TEST_DB_NAME}")
    yield test_db_conn

    test_db_conn.close()

    # Cleanup the test database after tests
    conn = psycopg2.connect(TEST_DB_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    # cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
    cur.close()
    conn.close()
