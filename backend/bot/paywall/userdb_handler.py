import psycopg2
from psycopg2 import sql
from functools import wraps
import pandas as pd



#needs to be modified for actual database
def db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
            user="bruce",
            password="",  # Add your password here if you've set one
            host="localhost",  # or 127.0.0.1
            port="5432",  # Default PostgreSQL port
            database="Testing"
            )
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except (Exception, psycopg2.Error) as error:
            print("Error:", error)
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
    return wrapper

@db_connection
def insert_user(cursor, user_id, referral, reffered_by):
    insert_query = sql.SQL("INSERT INTO users (user_id, Referrals,reffered_by  ) VALUES (%s, %s, %s)")
    cursor.execute(insert_query, (user_id, referral, reffered_by))
    print("Inserted data successfully")

@db_connection
def fetch_all_userdata(cursor):
    cursor.execute("SELECT * FROM users")
    records = cursor.fetchall()
    print("Data from users table:")
    for record in records:
        print(record)
    return records  # Optional, if you want to use the data elsewhere

@db_connection
def fetch_userspd(cursor):
    # Execute the query
    cursor.execute("SELECT * FROM users")
    
    # Fetch all records
    records = cursor.fetchall()
    
    # Get column names
    column_names = [desc[0] for desc in cursor.description]
    
    # Create a DataFrame with the data
    df = pd.DataFrame(records, columns=column_names)
    
    # Display the DataFrame
    print(df)
    
    return df 

@db_connection
def fetch_user_by_id(cursor, user_id):
    # Execute the query for a specific user
    query = sql.SQL("SELECT * FROM users WHERE user_id = %s")
    cursor.execute(query, (user_id,))
    
    # Fetch the records
    records = cursor.fetchall()
    
    # Get column names
    column_names = [desc[0] for desc in cursor.description]
    
    # Create a DataFrame with the data
    df = pd.DataFrame(records, columns=column_names)
    
    # Display the DataFrame
    print(df)
    
    return df 

@db_connection
def update_user(cursor, column_name, new_value, user_id):
    update_query = sql.SQL("UPDATE users SET {} = %s WHERE user_id = %s").format(
        sql.Identifier(column_name)
    )
    cursor.execute(update_query, (new_value, user_id))
    print("Data updated successfully")

@db_connection
def add_column(cursor, column_name, data_type):
    add_column_query = sql.SQL("""
        ALTER TABLE users
        ADD COLUMN {} {};
    """).format(
        sql.Identifier(column_name),
        sql.SQL(data_type)
    )
    
    cursor.execute(add_column_query)
    print("Column added successfully")
