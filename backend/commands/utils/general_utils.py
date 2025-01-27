import os
import requests
import time
import base58
import functools
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession, ClientError
from .token_utils import get_top_holders
from .wallet_utils import get_balance
import math
import aiohttp
import json
import ast
import itertools

#heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
quicknoderpc1 = os.environ.get('solrpc1')
quicknoderpc2 = os.environ.get('solrpc2')
quicknoderpc3 = os.environ.get('solrpc3')
quicknoderpc4 = os.environ.get('solrpc4')
#heliusrpc1 = os.environ.get('heliusrpc1')
birdeyeapi = os.environ.get('birdeyeapi')

# List of available RPCs
rpc_list = [quicknoderpc, quicknoderpc1, quicknoderpc2, quicknoderpc3, quicknoderpc4]
rpc_iterator = itertools.cycle(rpc_list)

async def get_rpc():
    global rpc_iterator
    return next(rpc_iterator)



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



async def get_top_traders(type:str = '1W', limit:int = 10000):
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





async def get_whales():
    """
    function that gets updated every x hours / days to fetch the top holders of sol, msol, usdc or usdt (whales)
    """
    days = 3
    with open('backend/commands/constants/whales.json', 'r') as f:
        whales = json.load(f)
        if ('timestamp' in whales and int(time.time()) - whales['timestamp'] < days * 24 * 60 * 60):
            if 'items' in whales:
                print("Returning cached data from 'whales.json'.")
                return set(whales['items'])
        else:
            print("Fetching new data for 'whales.json'.")
    whales = set()
    sol = "So11111111111111111111111111111111111111112"
    usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    usdt = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
    msol = "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"
    tokens = [sol, usdc, usdt, msol]
    sol_last_holder_balance = 0
    msol_last_holder_balance = 0
    usdc_last_holder_balance = 0
    usdt_last_holder_balance = 0
    for token in tokens:
        holders = await get_top_holders(token, 50)
        for index, holder in enumerate(holders):
            if index == len(holders) - 1:
                if token == sol:
                    print("ticker is sol, getting balance")
                    sol_last_holder_balance = await get_balance(holder['owner'], token)
                    print("sol_last_holder_balance", sol_last_holder_balance)
                elif token == msol:
                    msol_last_holder_balance = await get_balance(holder['owner'], token)
                elif token == usdc:
                    usdc_last_holder_balance = await get_balance(holder['owner'], token)
                elif token == usdt:
                    usdt_last_holder_balance = await get_balance(holder['owner'], token,)
            whales.add(holder['owner'])
    try:
        with open('backend/constants/whales.json', 'w') as f:
            json.dump({'timestamp': int(time.time()), sol: sol_last_holder_balance, msol: msol_last_holder_balance, usdc: usdc_last_holder_balance, usdt: usdt_last_holder_balance,
                       'items': list(whales)}, f, indent=4)
        print("Saved top holders to 'whales.json'.")
    except Exception as e:
        print(f"Error saving to 'whales.json': {e}")
    return whales
        

if __name__ == '__main__':
    # Test the timing_decorator
   asyncio.run(get_whales())
