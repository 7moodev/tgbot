import os
import requests
import time
import asyncio
import json
import random

heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
heliusrpc1 = os.environ.get('heliusrpc1')
birdeyeapi = os.environ.get('birdeyeapi')

# List of available RPCs
rpc_list = [heliusrpc, quicknoderpc, heliusrpc1]

# Variable to store the last used RPC
last_rpc = None

def get_rpc():
    global last_rpc

    # Filter out the last used RPC
    available_rpcs = [rpc for rpc in rpc_list if rpc != last_rpc]

    # Randomly select from available RPCs
    selected_rpc = random.choice(available_rpcs)
    
    # Update the last used RPC
    last_rpc = selected_rpc

    # Identify which RPC was selected
    if selected_rpc == heliusrpc:
        print("Using heliusrpc")
    elif selected_rpc == heliusrpc1:
        print("Using heliusrpc1")
    else:
        print("Using quicknoderpc")

    return selected_rpc
        
async def get_token_overview(token:str=None):
    print("Getting token overview for", token)
    """
    Get the overview of a token
    Costs 20 credits per requestww
    """
    if token is None:
        return None
    url = f"https://public-api.birdeye.so/defi/token_overview?address={token}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    response = requests.get(url, headers=headers)
    print("Returning token overview for", token)
    return response.json()


async def get_token_supply(token:str=None):
    print("Getting total supply for", token)
    """
    Get the total supply of a token
    Costs 0 credits per request
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "method": "getTokenSupply",
        "params": [token],
        "id": 1
    }

    response = requests.post(get_rpc(), headers=headers, json=data)
    if response.status_code != 200:
        return None
    print("Returning total supply for", token)
    print(response.json())
    return float(response.json()['result']['value']['uiAmount'])
    if response.status_code != 200:
        return None
    print("Returning total supply for", token)
    return float(response.json()['result']['value']['uiAmount'])


async def get_top_holders_with_constraint(token:str=None, min_value_usd:float=None, price:float=None):
    """
    Get the top holders of a token that hold at least min_value_usd worth of tokens
    
    Args:
        token (str): Token address
        min_value_usd (float): Minimum USD value of tokens that a holder must have
        price (float): Current price of token in USD
    
    Returns:
        list: List of holders that meet the minimum value constraint
    """
    if token is None:
        return None

    if min_value_usd is None or price is None:
        return None
        
    all_holders = []
    offset = 0
    batch_size = 100

    while True:
        url = f"https://public-api.birdeye.so/defi/v3/token/holder?address={token}&offset={offset}&limit={batch_size}"
        headers = {
            "accept": "application/json", 
            "chain": "solana",
            "X-API-KEY": birdeyeapi
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            if not response.json()['success']:
                return None
                
        batch = response.json()['data']['items']
        
        # Stop if we hit empty batch or zero amounts
        if not batch or batch[0]['amount'] == '0' or batch[-1]['amount'] == '0':
            break
            
        # Filter holders that meet minimum value
        for holder in batch:
            value_usd = float(holder['uiAmount']) * price
            if value_usd >= min_value_usd:
                all_holders.append(holder)
            else:
                # Since holders are ordered by amount, we can stop once we hit one below threshold
                return all_holders
                
        offset += batch_size
        
    return all_holders

async def get_price(token:str=None, unix_time:int = None):
    print("Getting price for", token, "at", unix_time)
    """
    Get the price of a token at a given unix time, costs 5 credits per request
    """		
    if unix_time is None:
        unix_time = int(time.time())
    if token is None:
        token = "So11111111111111111111111111111111111111112"
    url = f"https://public-api.birdeye.so/defi/historical_price_unix?address={token}&unixtime={unix_time}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    try:
        response = requests.get(url, headers=headers)
    except:
        print("Error getting price for", token, "at", unix_time, ":Birdeye")
        return None
    if response.status_code != 200:
        if response.json()['success'] == False:
            return None
    return response.json()['data']['value']
async def get_price_historical(token:str=None, type:str=None, start:int=None, end:int=None):
    print("Getting price historical for", token, "from", start, "to", end)
    """
    Get the price of a token at a given unix time, costs 5 credits per request
    """
    type = "1m"
    url = f"https://public-api.birdeye.so/defi/history_price?address={token}&address_type=token&type={type}&time_from={start}&time_to={end}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    try:
        response = requests.get(url, headers=headers)
    except:
        print("Error getting price historical for", token, "from", start, "to", end, ":Birdeye")
        return None
    if response.status_code != 200:
        if response.json()['success'] == False:
            return None
    return response.json()['data']['items']




async def get_token_creation_info(token:str=None):
    """{
  "data": {
    "txHash": "4ePtuFmo3uYX5m2mqMYEVqUpJzCoRHymmrTnCk1q1KiyvhpmCABVQ1sq1CFLMWHZAwbicC8V1Ao664WumAqxWQ86",
    "slot": 306705009,
    "tokenAddress": "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump",
    "decimals": 6,
    "owner": "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
    "blockUnixTime": 1733878974,
    "blockHumanTime": "2024-12-11T01:02:54.000Z"
  },"success": true}
"""
    print("Getting token creation info for", token)

    url = "https://public-api.birdeye.so/defi/token_creation_info?address={}".format(token)

    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY":birdeyeapi
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()['data']
    except Exception as e:
        print("Error getting token creation info for", token, ":Birdeye")
        return None


async def get_top_holders(token:str=None, limit = None):
    print("Getting top holders for", token, "with limit", limit)
    """
    Get the top holders of a token, costs 50 credits per request
    Iterates through all holders using offset pagination
    """	
    if(limit == 0):
        if os.path.exists('top_holders.json'):
            with open('top_holders.json', 'r') as file:
                print("Returning cached data from 'top_holders.json'")
                return json.load(file)
    all_holders = []
    if token is None:
        return True
    
    offset = 0
    batch_size = 100 if limit is None or limit > 100 else limit
    res = []
    
    while True:
        url = f"https://public-api.birdeye.so/defi/v3/token/holder?address={token}&offset={offset}&limit={batch_size}"
        headers = {
            "accept": "application/json",
            "chain": "solana",
            "X-API-KEY": birdeyeapi
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            if response.json()['success'] == False:
                return None
        batch = response.json()['data']['items']
        if not batch or batch[0]['amount'] == '0' or batch[len(batch)-1]['amount'] == '0':
            if len(all_holders) == 0:
                all_holders.extend(batch)
            break
        #print(len(batch))
        all_holders.extend(batch)
        # If we have a limit and reached/exceeded it, trim and break
        if limit is not None and len(all_holders) >= limit:
            all_holders = all_holders[:limit]
            break
        # If this batch was smaller than requested, we've got all holders
        if len(batch) < batch_size:
            break
        # Only continue if we need all holders
        if limit is None or len(all_holders) < limit:
            offset += batch_size
        else:
            break
    for holder in all_holders:
        res.append(holder['owner'])
    try:
        with open('top_holders.json', 'w') as file:
            json.dump(all_holders, file, indent=4)
        print(f"Saved top {len(res)} holders for {type} to 'top_holders.json'.")
    except Exception as e:
        print(f"Error saving to 'top_holders.json': {e}")
    print("Returning top holders for", token)
    print("Returned", len(all_holders), "holders")
    return all_holders



if __name__ == "__main__":
    #print(asyncio.run(get_top_holders("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", 100)))
   print(asyncio.run(get_token_supply("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump")))
   # print(asyncio.run(get_top_holders("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", 0)))
    # holders = asyncio.run(get_top_holders("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 500))
    # holders1 = asyncio.run(get_top_holders("So11111111111111111111111111111111111111112", 750))
    # save_to_path = "backend\commands\db\whales.json"
    # temp = []
    # for holder in holders:
    #     temp.append(holder['owner'])

    # for holder in holders1:
    #     temp.append(holder['owner'])
    # temp = list(set(temp))
    # with open(save_to_path, 'w') as f:
    #      json.dump(temp, f)
    # print(holders1)

