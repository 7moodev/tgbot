
from datetime import datetime
import json
from typing import Any

from backend.bot.parser import check_noteworthy
from backend.commands.utils.services.log_service import LogService

console = LogService("XBOT")

def extract_json(input: str):
    index = input.find("\"symbols\"")
    while index != -1 and input[index] != "{":
        index = input[:index].rfind("{")

    end_index = input.rfind("}")
    if end_index != -1:
        input = input[:end_index + 1]
    if index != -1 and end_index != -1:
        json_str = input[index:end_index+1]
        try:
            as_json = json.loads(json_str)
            console.log("as_json: ", as_json)
        except json.JSONDecodeError as e:
            console.log("JSONDecodeError: ", e)
    else:
        console.log("No JSON found")

    return as_json

def save_to_json(trending_tokens, file_name: str = ''):
    timestamp = datetime.now().replace(microsecond=0)
    # file_path = f"backend/commands/outputs/{file_name}_{timestamp}.json"
    file_path = f"backend/commands/outputs/{file_name}.json"
    with open(file_path, "w") as f:
        json.dump(trending_tokens, f, indent=4) # fmt: skip

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
    amount_of_whales = 0
    top_holders= top_holder_holdings['items']
    noteworthy = check_noteworthy(top_holders)
    for holder in noteworthy:
        dollar_token_share = holder['net_worth']- holder['net_worth_excluding']
        if dollar_token_share > 100_000:
            amount_of_whales += 1
    return amount_of_whales
