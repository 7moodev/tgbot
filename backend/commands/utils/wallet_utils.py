import httpx
import os
import asyncio
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
from .token_utils import get_price, get_price_historical, get_token_supply
from bisect import bisect_left
from aiohttp import ClientSession, ClientError
import aiohttp 
import random
import itertools
MAX_SIGNATURES = 2500

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


async def get_balance_birdeye(wallet, token):
    print("Getting balance using Birdeye for", wallet, "in", token)

    url = f"https://public-api.birdeye.so/v1/wallet/token_balance?wallet={wallet}&token_address={token}"

    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()['data']
        print(f"Fetched balance for wallet {wallet} in {token}")
        return data
    except Exception as e:
        print(f"Error fetching balance using Birdeye for wallet {wallet} in {token}: {str(e)}")
        return None    

async def get_balance(wallet: str, token: str = None, client: httpx.AsyncClient = None):
    timeout=0.25

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
            response = requests.post(await get_rpc(), headers=headers, json=data, timeout=timeout)
        else:
            response = await client.post(await get_rpc(), headers=headers, json=data, timeout=timeout)
    except Exception as e:
        print("Error getting balance for", wallet, "in", token, ":Solana RPC")
        return None

    if response.status_code != 200:
        return None

    if token:
        result = response.json().get('result', {}).get('value', [])
        if not result:
            if token == "So11111111111111111111111111111111111111112":
                return await get_balance(wallet=wallet)  # Get SOL balance
            return 0  # No token balance
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
async def calculate_avg_exit(token_address, data):
    supply = await get_token_supply(token_address)
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
            "avg_exit_price": avg_exit_price * supply,
            'total_amount':total_amount_sold,
            "oldest_trade_time": oldest_trade_time,
            "oldest_tx_hash": oldest_tx_hash
        }


async def calculate_avg_entry(token_address, data ):
    supply = await get_token_supply(token_address)
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
        return {"avg_entry_price":avg_entry_price * supply, 'total_amount':total_amount, "sniped_pfun":sniped_pfun,
                 "sniper_pfun_price":sniper_pfun_price * supply, "sniper_pfun_unix_time":sniper_pfun_unix_time,
                 "sniper_pfun_hash":sniper_pfun_hash,
                   "oldest_trade_time":oldest_trade_time, "oldest_tx_hash":oldest_tx_hash}
    else:
        return {"avg_entry_price":avg_entry_price * supply,'total_amount':total_amount, "sniped_pfun":sniped_pfun, "oldest_trade_time":oldest_trade_time, "oldest_tx_hash":oldest_tx_hash}

async def calculate_avg_holding(entry_data, exit_data):
    print("Calculating average holding (break-even) price out of entry and exit data")
    """
    Calculate the "new average" or break-even price of the current holding from a trading perspective.

    Parameters:
    - entry_data: dict containing results from calculate_avg_entry function, 
                  including:
                    'avg_entry_price' (float): your original buy/entry price 
                    'total_amount' (float): total tokens purchased
    - exit_data: dict containing results from calculate_avg_exit function, 
                 including:
                    'avg_exit_price' (float): (average) price at which tokens were sold
                    'total_amount' (float): total tokens sold

    Returns:
    - dict: {
        "avg_holding_price": float,  
            # Break-even price for the REMAINING tokens.  If 0 => no tokens left.
        "current_holding_amount": float,  
            # Number of tokens still held after partial sells (can be 0 or negative).
        "rebuy_detected": bool  
            # Whether user sold some tokens and then bought again afterward
      }
    """
    # Extract values from input data
    avg_entry_price = entry_data.get("avg_entry_price", 0.0)
    total_buy_amount = entry_data.get("total_amount", 0.0)
    avg_exit_price = exit_data.get("avg_exit_price", 0.0)
    total_sell_amount = exit_data.get("total_amount", 0.0)
    avg_entry_cost = avg_entry_price * total_buy_amount
    avg_exit_cost = avg_exit_price * total_sell_amount
    current_holding_amount = total_buy_amount - total_sell_amount
    if (avg_entry_cost == 0 or current_holding_amount == 0):
        return {
            "avg_holding_price": 0.0,  # No holdings, break-even doesn't apply
            "current_holding_amount": current_holding_amount,
            "rebuy_detected": False,
            "label": "No Buys"
        }
    if (avg_exit_cost == 0):
        return {
            "avg_holding_price": avg_entry_price,  # No sells, break-even is the entry price
            "current_holding_amount": current_holding_amount, # to check, if current holding = this, then normal, otherwise funded
            "rebuy_detected": False,
            "label": None
        }
    #21488934*21700
    #956549*18048674
    
    avg_break_even = (avg_entry_cost - avg_exit_cost) / current_holding_amount
    if (current_holding_amount <= 0):
        return {
            "avg_holding_price": avg_entry_price,  # No holdings, break-even doesn't apply
            "current_holding_amount": current_holding_amount,
            "rebuy_detected": False,
            "label": "Funded"
        }
    if (avg_break_even < 0):
        return {
            "avg_holding_price": avg_entry_price,  # No holdings, break-even doesn't apply
            "current_holding_amount": current_holding_amount,
            "rebuy_detected": False,
            "label": "Normal"
        }
    return  {
        "avg_holding_price": avg_break_even,
        "current_holding_amount": current_holding_amount,
        "rebuy_detected": False,
        "label": "Normal"
    }




async def get_wallet_age(wallet: str = None, max_signatures: int = 20000, max_age:int = None,  bot_filter: bool = True, time_out: int = None):
    """
    Get the blocktime of the oldest transaction of a wallet in unix time.
    Returns 0 for exchanges or bot activity.
    """
    print("Getting wallet age for", wallet)
    if wallet is None:
        return None

    headers = {"Content-Type": "application/json"}
    all_signatures_count = 0
    oldest_block_time = None
    before = None
    time_now_unix = int(time.time())
    oldest = None
    async with httpx.AsyncClient() as client:
        while True:
            if max_age:
                if oldest_block_time and oldest_block_time < time_now_unix - max_age:
                    return oldest
            # Exit if max_signatures is exceeded
            if all_signatures_count > max_signatures:
                return oldest

            # Prepare request payload
            params = [wallet, {"limit": 1000}]
            if before:
                params[1]["before"] = before
            data = {"jsonrpc": "2.0", "method": "getSignaturesForAddress", "params": params, "id": 1}

            try:
                # Make asynchronous request
                     # Make asynchronous request
                response = await client.post(await get_rpc(), headers=headers, json=data, timeout=time_out)
                response.raise_for_status()
                result = response.json().get('result', [])

                if not result:  # No more signatures
                    break

                # Update the count and check for bot activity
                all_signatures_count += len(result)
                if bot_filter and time_now_unix - result[-1].get('blockTime', 0) < 72000:
                    return 0
                # Update oldest block time and before signature
                oldest = result[-1]
                before = oldest['signature']
                oldest_block_time = oldest.get('blockTime', oldest_block_time)

                # Exit early if fewer than 1000 results are returned
                if len(result) < 1000:
                    break
            except (httpx.RequestError, KeyError, httpx.HTTPStatusError) as e:
                print(response.json())
                print(f"Error fetching wallet age for {wallet}: {str(e)}")
                return None

    print("Returning wallet age for", wallet)
    return oldest
async def get_wallet_age_readable(wallet:str=None, time_in_unix=None):
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
                        async with session.post(await get_rpc(), headers=headers, json=data) as response:
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
    hist = asyncio.run(get_wallet_trade_history('Fnz5CaHjX8SBuJAL6cKwLVY6QnAT7o5HNxz47qbYzMMW', 100, 0, 0))
    entry = asyncio.run(calculate_avg_entry( "6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump", hist))
    exit = asyncio.run(calculate_avg_exit("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump",hist))
    holding = asyncio.run(calculate_avg_holding(entry, exit))
    with open("wtf11.json", 'w') as f:  
        holding = {'holding': holding, 'entry': entry, 'exit': exit, 'hist': hist}
        json.dump(holding, f, indent=4)
    # print(entry)
    # print(exit)
    # holding = calculate_avg_holding(entry_data=entry, exit_data=exit)
    # print(holding)
    #print(asyncio.run(get_wallet_age("Hq2nUyT8VxgNcrgQM7eBA69iPp2jQvNCT7iycDqL3RJg")))
    #wtf = asyncio.run(get_wallet_trade_history("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF", limit=1000, after_time=1737332294))

    #print(exit)
    # with open("wtf1.json", 'w') as f:  
    #     json.dump(wtf, f, indent=4)
    #print(asyncio.run(get_wallet_portfolio("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF")))
    #print(asyncio.run(get_balance("4A7kWzk5wGxXaJCQC8kw7B17hSqGK9YVCoc2yxSedfS3", "So11111111111111111111111111111111111111112")))