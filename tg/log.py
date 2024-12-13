# this script is intended to log every entry that is received by the bot and to save it to a sqlite database
import os
import csv
import time
import sqlite3
def log_entry(entry=None,command=None,content=None):
    # Create database connection
    conn = sqlite3.connect('user_logs.db')
    cursor = conn.cursor()
    # Convert Telegram Message object to dictionary
    entry_dict = {
        'message_id': entry.message_id,
        'date': str(entry.date),
        'text': entry.text,
        'from_user_id': entry.from_user.id,
        'is_bot': entry.from_user.is_bot,
        'from_user_username': entry.from_user.username,
        'from_user_first_name': entry.from_user.first_name,
        'from_user_last_name': entry.from_user.last_name,
        'from_user_language_code': entry.from_user.language_code,
        'from_user_can_join_groups': entry.from_user.can_join_groups,
        'from_user_can_read_all_group_messages': entry.from_user.can_read_all_group_messages,
        'from_user_supports_inline_queries': entry.from_user.supports_inline_queries,
        'from_user_is_premium': entry.from_user.is_premium,
        'from_user_added_to_attachment_menu': entry.from_user.added_to_attachment_menu,
        'from_user_has_main_web_app': entry.from_user.has_main_web_app,
        'date': str(entry.date),
        'chat': entry.chat,
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
    CREATE TABLE IF NOT EXISTS general_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        {columns}
    )
    '''
    if command is not None:
        specific_log(command,entry,content)
    cursor.execute(create_table_sql)
    # Insert the data
    columns = ', '.join([f'"{k}"' for k in flat_data.keys()])
    placeholders = ', '.join(['?' for _ in flat_data.keys()])
    insert_sql = f'INSERT INTO general_logs ({columns}) VALUES ({placeholders})'
    
    cursor.execute(insert_sql, list(flat_data.values()))
    
    # Commit and close
    conn.commit()
    conn.close()

def specific_log(command,entry,content):
    print(command)
    print(content)
    
    conn = sqlite3.connect('user_logs.db')
    cursor = conn.cursor()
    entry_dict = {
        'content': content,
        'message_id': entry.message_id,
        'date': str(entry.date),
    }
    flat_data = {}
    def flatten_dict(d, parent_key=''):
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                flatten_dict(v, new_key)
            else:
                flat_data[new_key] = str(v) if v is not None else None
    flatten_dict(entry_dict)
    columns = ', '.join([f'"{k}"' for k in flat_data.keys()])
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS {command} (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        {columns}
    )
    '''
    cursor.execute(create_table_sql)
    columns = ', '.join([f'"{k}"' for k in flat_data.keys()])
    placeholders = ', '.join(['?' for _ in flat_data.keys()])
    insert_sql = f'INSERT INTO {command} ({columns}) VALUES ({placeholders})'
    cursor.execute(insert_sql, list(flat_data.values()))
    conn.commit()
    conn.close()
