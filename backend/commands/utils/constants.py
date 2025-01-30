import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
commands_output_path = os.path.join(root_path, 'backend/commands/outputs')

DB_PATH = os.path.join(root_path, 'backend/db')
DB_PATH_TAMAGO = os.path.join(DB_PATH, 'user_logs_tamago.db')
DB_REL_PATH_TAMAGO = 'db/user_logs_tamago.db'
print(DB_PATH_TAMAGO)
