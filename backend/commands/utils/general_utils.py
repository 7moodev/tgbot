import os
import requests
import time
import base58
import functools
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession, ClientError
import math
import aiohttp
import json
import ast


heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
heliusrpc1 = os.environ.get('heliusrpc')
birdeyeapi = os.environ.get('birdeyeapi')
def timing_decorator(func):
    # Track recursion depth to create indented output for nested calls
    timing_decorator.level = getattr(timing_decorator, 'level', 0)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        indent = "  " * timing_decorator.level
        timing_decorator.level += 1
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.time()
            timing_decorator.level -= 1
        
        execution_time = end_time - start_time
        print(f"{indent}Function '{func.__name__}' took {execution_time:.2f} seconds to execute")
        return result
    return wrapper

def get_rpc():
    Random = random.randint(0, 2)
    if Random == 0:
        print("Using heliusrpc")
        return heliusrpc
    elif Random == 1:  
        print("Using heliusrpc1")
        return heliusrpc1
    else:
        print("Using quicknoderpc")
        return quicknoderpc
        


async def get_top_traders(type:str = '1W', limit:int = 20):
    # Costs 30 per call
    print(f"Getting top {limit} for {type}")
    # if(limit == 0): #for testing
    #     array_of_objects = ast.literal_eval(example_output)
    #     # Convert each dictionary in the list to a JSON string
    #     array_of_json = [json.dumps(d) for d in array_of_objects]
    #     return array_of_json
    all_data = {}
    if os.path.exists('top_traders.json'):
        with open('top_traders.json', 'r') as file:
            try:
                all_data = json.load(file)
            except json.JSONDecodeError:
                print("Error loading 'top_traders.json'. File is empty or corrupt.")
                all_data = {}
            for item in all_data.get('items',[]):
                if (int(time.time() - item.get('timestamp', 0)) < 7 * 24 * 60 * 60) and (item.get('type', '') == type):
                    print("Returning cached data from 'top_traders.json'.")
                    return item.get('items', [])
    res = []
    while(len(res) < limit):

        url = f"https://public-api.birdeye.so/trader/gainers-losers?type={type}&sort_by=PnL&sort_type=desc&offset={len(res)}&limit=10"
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            'X-API-KEY': birdeyeapi
        }
        response = requests.get(url, headers=headers)
        if (response.status_code != 200):
            print("Error getting top traders: ", response.json())
            return res
        res += response.json()['data']['items']
    current_timestamp = str(int(time.time()))
    try:
        if("items" not in all_data):
            all_data["items"] = []
        all_data["items"].append({
            "timestamp": int(current_timestamp),
            "type": type,
            "limit": limit,
            "items": res,
        })
    except NameError:
        print("Creating new saved_data dictionary.")
    try:
        with open('top_traders.json', 'w') as file:
            json.dump(all_data, file, indent=4)
        print(f"Saved top {len(res)} traders for {type} to 'top_traders.json'.")
    except Exception as e:
        print(f"Error saving to 'top_traders.json': {e}")
    print("Returning top {} traders for {}".format(limit, type))
    return res



async def get_token_largest_accounts(token_mint_address):
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            token_mint_address
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Failed to fetch data with status code {response.status_code}")
        return None



if __name__ == '__main__':
    # Test the timing_decorator
    #print(asyncio.run(get_top_traders(limit = 1000)))
    print(asyncio.run(get_token_largest_accounts("8ghZ1x6QCMzabdvze7ycXU83Jg13PFopSTii3vZEpump")))
