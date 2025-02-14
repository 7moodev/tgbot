import pytest
from backend.database.token_holders_database import TokenHoldersDatabase

import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, root_path)


tokenHolderDb = TokenHoldersDatabase()


# class TestTokenHoldersDatabase:
#     @pytest.mark.only
#     def test_create_table(self):
#         assert True == False
#         # try:
#         #     with self.connect_db() as conn:
#         #         cursor = conn.cursor()
#         #         cursor.execute(create_table_sql)
#         # finally:
#         #     if self.conn:
#         #         cursor.close()
#         #         self.conn.close()


@pytest.mark.only
def test_create_admin_table(test_db):
    # Open a cursor to perform database operations
    cur = test_db.cursor()

    print(">>> Creating table test")
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

    # Query the database and obtain data as Python objects.
    cur.execute("SELECT * FROM test")
    cur.fetchone()
    # will return (1, 100, "abc'def")

    # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the cursor
    for record in cur:
        print(record)
