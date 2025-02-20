
from datetime import datetime
import json
import re
from typing import Any

from backend.bot.parser import check_noteworthy
from backend.commands.utils.api.entities.token_entities import TokenEntity
from backend.commands.utils.services.log_service import LogService

console = LogService("XBOT")

def extract_json(input: str) -> dict | None:
    json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    matches = re.findall(json_pattern, input, re.DOTALL)
    for json_str in reversed(matches):
        try:
            parsed_json = json.loads(json_str)
            if "symbols" in parsed_json and "closings" in parsed_json:
                return parsed_json
        except json.JSONDecodeError:
            continue

# keep track of file_names, I want to aggregate all the data into one file, when I execute the program. After every restart reset the json to []
log_tracker_map = {}
def save_to_json(data: list[Any], file_name: str = ''):
    # timestamp = datetime.now().replace(microsecond=0)
    # file_path = f"backend/commands/outputs/{file_name}_{timestamp}.json"
    file_path = f"backend/commands/outputs/{file_name}.json"
    # Reset file content on first call
    if not file_name in log_tracker_map:
        with open(file_path, "w") as f:
            json.dump([], f, indent=4) # fmt: skip
        log_tracker_map[file_name] = 0
    else:
        # Counter for tracking
        if log_tracker_map[file_name] == 0:
            log_tracker_map[file_name] += 1
        else:
            log_tracker_map[file_name] = 0
        with open(file_path, "r") as f:
            as_json = json.load(f)
        if isinstance(as_json, list) and isinstance(data, list):
            data = as_json + data
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4) # fmt: skip

def get_from_json(file_name: str = ''): # fmt: skip
    with open(f"backend/commands/outputs/{file_name}.json", "r") as f:
        as_json = json.load(f)
    return as_json

def exists_json(file_name: str = ''):
    try:
        with open(f"backend/commands/outputs/{file_name}.json", "r") as f:
            return True
    except FileNotFoundError:
        return False

def get_amount_of_whales(top_holder_holdings: list[Any]) -> int:
    top_holders= top_holder_holdings['items']
    noteworthy = check_noteworthy(top_holders)
    return len(noteworthy)

def get_name_symbol_address(tokens: list[TokenEntity]) -> list[str]:
    converted = [f"{t['name']} ({t['symbol']}) - {t['address']}" for t in tokens]
    return converted

if __name__ == "__main__":
    save_to_json(['one'], file_name="testi")
    save_to_json(['two'], file_name="testi")

# python -m backend.xBot.x_bot_utils
