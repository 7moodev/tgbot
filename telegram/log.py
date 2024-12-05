# this script is intended to log every entry that is received by the bot and to save it to a sqlite database

import os
import csv
import time
import sqlite3



def log_entry(entry):
    # Create database connection
    conn = sqlite3.connect('telegram_logs.db')
    cursor = conn.cursor()
    
    # Convert Telegram Message object to dictionary
    entry_dict = {
        'message_id': entry.message_id,
        'date': str(entry.date),
        'text': entry.text,
        'from_user_id': entry.from_user.id,
        'from_user_username': entry.from_user.username,
        'from_user_first_name': entry.from_user.first_name,
        'from_user_last_name': entry.from_user.last_name,
        'chat_id': entry.chat.id,
        'chat_type': entry.chat.type,
    }
    
    # Flatten the dictionary (in case we need it for future nested structures)
    flat_data = {}
    
    def flatten_dict(d, parent_key=''):
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            
            # Handle nested dictionaries
            if isinstance(v, dict):
                flatten_dict(v, new_key)
            # Handle None values and other types
            else:
                flat_data[new_key] = str(v) if v is not None else None
    
    # Flatten the entry dictionary
    flatten_dict(entry_dict)
    
    # Create table if it doesn't exist
    columns = ', '.join([f'"{k}" TEXT' for k in flat_data.keys()])
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS telegram_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        {columns}
    )
    '''
    cursor.execute(create_table_sql)
    
    # Insert the data
    columns = ', '.join([f'"{k}"' for k in flat_data.keys()])
    placeholders = ', '.join(['?' for _ in flat_data.keys()])
    insert_sql = f'INSERT INTO telegram_logs ({columns}) VALUES ({placeholders})'
    
    cursor.execute(insert_sql, list(flat_data.values()))
    
    # Commit and close
    conn.commit()
    conn.close()
    
    