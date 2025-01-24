import httpx
import os
import asyncio
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
from .token_utils import get_price, get_price_historical
from bisect import bisect_left
from aiohttp import ClientSession, ClientError
import aiohttp 
import random
MAX_SIGNATURES = 2500

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

async def get_balance(wallet: str, token: str = None, client: httpx.AsyncClient = None):

    """
    Get the balance of a wallet in SOL or a token
    """
    if token:
        print("Getting balance for", wallet, "in", token)
    else:
        print("Getting balance for", wallet, "in SOL")

    headers = {"Content-Type": "application/json"}
    if token:
        # Get token balance
        data = {
            "jsonrpc": "2.0",
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet,
                {"mint": token},
                {"encoding": "jsonParsed"}
            ],
            "id": 1
        }
    else:
        # Get SOL balance
        data = {
            "jsonrpc": "2.0",
            "method": "getBalance",
            "params": [wallet],
            "id": 1
        }
    
    try:
        if client is None:
            response = requests.post(get_rpc(), headers=headers, json=data)
        else:
            response = await client.post(get_rpc(), headers=headers, json=data)
    except:
        print("Error getting balance for", wallet, "in", token, ":Solana RPC")
        return None

    if response.status_code != 200:
        return None

    if token:
        result = response.json().get('result', {}).get('value', [])
        if not result:
            return 0
        token_amount = float(result[0]['account']['data']['parsed']['info']['tokenAmount']['amount'])
        decimals = result[0]['account']['data']['parsed']['info']['tokenAmount']['decimals']
        if token == "So11111111111111111111111111111111111111112":
            return (token_amount / (10 ** decimals)+ await get_balance(wallet=wallet))  # Convert lamports to SOL
        return token_amount / (10 ** decimals)
    else:
        balance = response.json().get('result', {}).get('value', 0)
        return balance / (10 ** 9)  # Convert lamports to SOL
    


async def get_wallet_portfolio(wallet: str):
    """
    Fetch wallet portfolio with rate limiting and error handling
    
    :param wallet: Wallet address to fetch portfolio for
    :return: Portfolio data or error dict
    """
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi  # Assumes birdeyeapi is defined elsewhere
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        
        data = response.json()['data']
        print(f"Fetched portfolio for wallet {wallet}")
        return data
    except Exception as e:
        return {"error": f"Exception fetching portfolio for wallet {wallet}: {str(e)}"}








    
async def get_wallet_trade_history(wallet:str, limit:int=100, before_time:int=0, after_time:int=0):

    if (limit == 0):
        if os.path.exists('trade_history.json'):
            with open('trade_history.json', 'r') as file:
                data = json.load(file)
                print("Returning cached data from 'trade_history.json'.")
                return data
    print("Getting trade history for", wallet)
    res = []
    while(len(res) < limit):
        url = f"https://public-api.birdeye.so/trader/txs/seek_by_time?address={wallet}&offset={len(res)}&limit=100&tx_type=swap&before_time={before_time}&after_time={after_time}"
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": birdeyeapi
        }
        response = requests.get(url, headers=headers)
        if (response.status_code != 200):
            print("Error getting trade_history: ", response.json())
            return res
        res += response.json()['data']['items']
        if len(response.json()['data']['items']) < 100:
            break
    # try:
    #     with open('trade_history.json', 'w') as file:
    #         json.dump(res, file, indent=4)
    #     print(f"Saved trade history for {wallet} to 'trade_history.json'.")
    # except Exception as e:
    #     print(f"Error saving to 'top_holders.json': {e}")
    print("Returning trade history for", wallet)
    return res
def calculate_avg_exit(token_address, data):
    print("Calculating average exit price for", token_address)
    total_revenue = 0
    total_amount_sold = 0
    oldest_trade_time = int(time.time())
    oldest_tx_hash = ""

    for trade in data:
        base = trade["base"]
        quote = trade["quote"]
        price = trade['base_price'] if trade.get('base_price') else trade['quote_price']
        quote_address = quote["address"]
        base_address = base["address"]
        quote_type_swap = quote["type_swap"]
        base_type_swap = base["type_swap"]
        trade_time = trade['block_unix_time']

        # Check if the token is in "from" direction
        if quote_address == token_address and quote_type_swap == "from":
            price = quote.get('price', 0) if quote.get('price') else quote.get('nearest_price', 0)
            amount = quote["ui_amount"]
            total_revenue += amount * price
            total_amount_sold += amount
        elif base_address == token_address and base_type_swap == "from":
            price = base.get('price', 0) if base.get('price') else base.get('nearest_price', 0)
            amount = base["ui_amount"]
            total_revenue += amount * price
            total_amount_sold += amount
        
        if ((quote_address == token_address and quote_type_swap == "from") or 
            (base_address == token_address and base_type_swap == "from")):
                if trade_time < oldest_trade_time:
                    oldest_trade_time = trade_time
                    oldest_tx_hash = trade['tx_hash']
    
    # Calculate average sell price
    if total_amount_sold > 0:
        avg_exit_price = total_revenue / total_amount_sold
    else:
        avg_exit_price = 0  # No exits for the token
    print("Returning average exit price for", token_address)
    return {
            "avg_exit_price": avg_exit_price,
            'total_amount':total_amount_sold,
            "oldest_trade_time": oldest_trade_time,
            "oldest_tx_hash": oldest_tx_hash
        }


def calculate_avg_entry(token_address, data ):
    print("Calculating average entry price for", token_address)
    total_cost = 0
    total_amount = 0
    sniped_pfun=False
    sniper_pfun_price=0
    sniper_pfun_unix_time=0 
    sniper_pfun_hash=""
    oldest_trade_time=int(time.time())
    oldest_tx_hash=""
    for trade in data:
        base = trade["base"]
        quote = trade["quote"]
        price = trade['base_price'] if trade.get('base_price') else trade['quote_price']    
        quote_address = quote["address"]
        base_address = base["address"]
        quote_type_swap = quote["type_swap"]
        base_type_swap = base["type_swap"]
        trade_time = trade['block_unix_time']
        # Check if the token is in "to" direction
        if quote_address == token_address and quote_type_swap == "to":
            price = quote.get('price',0) if quote.get('price') else quote.get('nearest_price', 0)
            amount = quote["ui_amount"]
            if not price:
                continue
            total_cost += amount * price
            total_amount += amount
        elif base_address == token_address and base_type_swap == "to":
            price = base.get('price',0) if base.get('price') else base.get('nearest_price', 0)
            if not price:
                continue
            amount = base["ui_amount"]
            
            total_cost += amount * price
            total_amount += amount
        if((quote_address == token_address and quote_type_swap=="to") or (base_address == token_address and base_type_swap=="to")):
            if(trade['source']=='pump_dot_fun'):
                sniped_pfun=True
                sniper_pfun_price=price
                sniper_pfun_unix_time=trade_time
                sniper_pfun_hash=trade['tx_hash']
            if trade_time<oldest_trade_time:
                oldest_trade_time=trade_time
                oldest_tx_hash=trade['tx_hash']
    
    # Calculate average price
    if total_amount > 0:
        avg_entry_price = total_cost / total_amount
    else:
        avg_entry_price = 0  # No entries for the toke
    print("Returning average entry price for", token_address)
    if sniped_pfun:
        return {"avg_entry_price":avg_entry_price, 'total_amount':total_amount, "sniped_pfun":sniped_pfun,
                 "sniper_pfun_price":sniper_pfun_price, "sniper_pfun_unix_time":sniper_pfun_unix_time,
                 "sniper_pfun_hash":sniper_pfun_hash,
                   "oldest_trade_time":oldest_trade_time, "oldest_tx_hash":oldest_tx_hash}
    else:
        return {"avg_entry_price":avg_entry_price,'total_amount':total_amount, "sniped_pfun":sniped_pfun, "oldest_trade_time":oldest_trade_time, "oldest_tx_hash":oldest_tx_hash}

def calculate_avg_holding(entry_data, exit_data):
    print("Calculating average holding price out of entry and exit data")
    """
    Calculate the average price of the current holding.

    Parameters:
    - entry_data: dict containing results from calculate_avg_entry function, 
                  including 'avg_entry_price' and 'total_amount' (total buy amount).
    - exit_data: dict containing results from calculate_avg_exit function, 
                 including 'avg_exit_price' and 'total_amount' (total sell amount).
    Returns:
    - dict: {
        "avg_holding_price": float,  # Average price of the current holding, if 0 meaning wallet got funded
        "current_holding_amount": float,  # Current amount of the token held, if negative then it's funded amount
        "rebuy_detected": bool  # Whether a rebuy after selling has occurred
      }
    """
    # Extract values from input data
    avg_entry_price = entry_data.get("avg_entry_price", 0)
    total_buy_amount = entry_data.get("total_amount", 0)
    avg_exit_price = exit_data.get("avg_exit_price", 0)
    total_sell_amount = exit_data.get("total_amount", 0)

    # Calculate current holdings
    current_holding_amount = total_buy_amount - total_sell_amount

    # Handle cases where there's no holding left
    if current_holding_amount <= 0:
        return {
            "avg_holding_price": 0,  # No holdings, average price is zero
            "current_holding_amount": current_holding_amount,
            "rebuy_detected": False
        }

    # Detect rebuy: true if sold some tokens and then bought again
    rebuy_detected = total_sell_amount > 0 and total_buy_amount > total_sell_amount

    # Calculate the total cost of current holdings
    total_cost_of_holdings = (avg_entry_price * total_buy_amount) - (avg_exit_price * total_sell_amount)

    # Calculate average price of the current holding
    avg_holding_price = total_cost_of_holdings / current_holding_amount
    print("Returning average holding price out of entry and exit data")
    return {
        "avg_holding_price": avg_holding_price,
        "current_holding_amount": current_holding_amount,
        "rebuy_detected": rebuy_detected
    }




async def get_wallet_age(wallet:str=None,  max_signatures:int=MAX_SIGNATURES, bot_filter:bool=True):
    print("Getting wallet age for", wallet)
    """
    Get the blocktime of the oldest transaction of a wallet in unix time. 
    Returns 0 for exchanges
    Costs 0 credits
    """	
    if wallet is None:
        return None
    headers = {
        "Content-Type": "application/json",
    }
    all_signatures = []
    before = None
    while True:
        time_nowin_unix = int(time.time())
        if all_signatures:
            bot_check = bot_filter and time_nowin_unix - all_signatures[-1].get('blockTime') < 72000
        else:
            bot_check = False
        if len(all_signatures) > max_signatures or bot_check:
            return 0
        params = [wallet, {"limit": 1000}]
        if before:
            params[1]["before"] = before
        data = {
            "jsonrpc": "2.0",
            "method": "getSignaturesForAddress", 
            "params": params,
            "id": 1
        }
        response = requests.post(get_rpc(), headers=headers, json=data)
        if response.status_code != 200:
            print("Error fetching signatures for", wallet)
            return None
        result = response.json().get('result', [])
        if not result:
            break
        all_signatures.extend(result)
        if len(result) < 1000:
            break
        before = result[-1]['signature']
    # Return the blocktime of the last signature (oldest transaction)
    if all_signatures:
        return all_signatures[-1].get('blockTime')
    return None

def get_wallet_age_readable(wallet:str=None, time_in_unix=None):
    if time_in_unix is None:
        wallet_age_unix = get_wallet_age(wallet)
    else:
        wallet_age_unix = time_in_unix
    if wallet_age_unix == 0:
        return 'Exchange/LP'
    if wallet_age_unix is None:
        return None
    current_time = int(time.time())
    age_seconds = current_time - wallet_age_unix
    
    years = age_seconds // (365 * 24 * 60 * 60)
    months = age_seconds // (30 * 24 * 60 * 60)
    days = age_seconds // (24 * 60 * 60)
    hours = age_seconds // (60 * 60)
    minutes = age_seconds // 60
    
    if years > 0:
        return f"{years} year{'s' if years > 1 else ''}"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''}"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return f"{age_seconds} second{'s' if age_seconds > 1 else ''}"
    

semaphore = asyncio.Semaphore(10)

async def get_all_signatures(wallet: str = None, limit: int = None):
    print("Getting all signatures for", wallet)
    """
    Get the last signature of a wallet with retry logic.
    Costs 50 credits per request.
    """
    if wallet is None:
        return None
    headers = {
        "Content-Type": "application/json",
    }
    all_signatures = []
    before = None
    retries = 3  # Retry a few times before failing
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with semaphore:  # Respect rate limit by using the semaphore
                    while True:
                        if limit is not None and len(all_signatures) >= limit:
                            break
                        data = {
                            "jsonrpc": "2.0",
                            "method": "get_signatures_for_address",
                            "params": [wallet, {"limit": 1000, "before": before} if before else {"limit": 1000}],
                            "id": 1
                        }
                        async with session.post(get_rpc(), headers=headers, json=data) as response:
                            if response.status != 200:
                                print(f"Error fetching signatures for {wallet}, status code {response.status}")
                                return None
                            result = await response.json()
                            result = result.get('result', [])
                            if not result:
                                break
                            all_signatures.extend(result)
                            if len(result) < 1000:
                                break
                            before = result[-1]['signature']
                return all_signatures
            except ClientError as e:
                print(f"Error fetching signatures for {wallet}, attempt {attempt + 1}/{retries}: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
    return None

if __name__ == "__main__":
    # start_time = time.time()
    # asyncio.run(main())
    # print(f"Execution time: {time.time() - start_time} seconds")
    #print(get_wallet_age("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"))
    #print(asyncio.run(get_wallet_trade_history("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"],
                                            #  httpx.AsyncClient())))
    #print(asyncio.run(get_wallet_avg_price("7tco85pE38UHUmaSNZRnsvcw2GXJv5TowP1tSw3GAL6M", "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", "buy", httpx.AsyncClient())))
    #print(asyncio.run(get_all_signatures('UeXfwweGMBV8JkTQ7pFF6shPR9EiKEg8VnTNF4qKjhh')))
    #print(asyncio.run(get_balance('5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVh', '9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump')))
    # hist = asyncio.run(get_wallet_trade_history('713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF', 100, 0, 0))
    # entry = calculate_avg_entry(hist, "7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump")
    # exit = calculate_avg_exit(hist, "7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump")
    # print(entry)
    # print(exit)
    # holding = calculate_avg_holding(entry_data=entry, exit_data=exit)
    # print(holding)
    #print(asyncio.run(get_wallet_age("Hq2nUyT8VxgNcrgQM7eBA69iPp2jQvNCT7iycDqL3RJg")))
    # wtf = asyncio.run(get_wallet_trade_history("", limit=1000, after_time=1737332294))
    # print(len(wtf))
    # with open("wtf1.json", 'w') as f:  
    #     json.dump(wtf, f, indent=4)
    print(asyncio.run(get_wallet_portfolio("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF")))