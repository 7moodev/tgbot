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
birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
solscanapi = os.environ.get('solscan')
MAX_SIGNATURES = 5000
API_RATE_LIMIT = 15  # Max API calls per second
BATCH_SIZE = 15  # Maximum requests allowed per batch (aligned with rate limit)

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
    Random = random.randint(0, 1)
    if Random == 0:
        print("Using heliusrpc")
        return heliusrpc
    else:
        print("Using quicknoderpc")
        return quicknoderpc

def get_price(token:str=None, unix_time:int = None):
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
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        if response.json()['success'] == False:
            return None
    return response.json()['data']['value']
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
def get_wallet_age(wallet:str=None,  max_signatures:int=MAX_SIGNATURES, bot_filter:bool=True):
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
            bot_check = bot_filter and time_nowin_unix - all_signatures[-1].get('block_time') < 36000
        else:
            bot_check = False
        if len(all_signatures) > max_signatures or bot_check:
            return 0
        params = [wallet, {"limit": 1000}]
        if before:
            params[1]["before"] = before
        data = {
            "jsonrpc": "2.0",
            "method": "get_signatures_for_address", 
            "params": params,
            "id": 1
        }
        response = requests.post(get_rpc(), headers=headers, json=data)
        if response.status_code != 200:
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
        return all_signatures[-1].get('block_time')
    return None

async def fetch_wallet_portfolio(session, wallet: str):
    """
    Asynchronously fetch the wallet portfolio with rate limiting.
    """
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }

    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        data = await response.json()
        if not data.get('success', True):
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        return data

async def process_holder(count, holder, session, total_supply, token):
    """
    Process a single holder with adaptive pacing.
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100

    print(f"Processing holder {wallet}")
    portfolio = await fetch_wallet_portfolio(session, wallet)
    if "error" in portfolio:
        return {f'wallet {count}': portfolio}
    net_worth = round(portfolio['data']['total_usd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    token_item = next((item for item in holdings if item['address'] == token), None)
    net_worth_excluding = net_worth - (token_item['value_usd'] if token_item else 0)
    # Get top holdings efficiently
    top_holdings = holdings[:3]
    
    return {
            f'wallet {count}': {
                'wallet': wallet,
                'amount': amount,
                'share_in_percent': round(share_in_percent, 3),
                'net_worth': net_worth,
                'net_worth_excluding': net_worth_excluding,
                'first_top_holding': top_holdings[0] if len(top_holdings) > 0 else None,
                'second_top_holding': top_holdings[1] if len(top_holdings) > 1 else None,
                'third_top_holding': top_holdings[2] if len(top_holdings) > 2 else None,
            }
        }

async def get_top_holders_ready(token: str = None, limit: int = 50):
    """
    Get the info of the top holders of a token with adaptive pacing for API requests.
    """
    if token is None:
        return None

    print(f"Getting top holders info for {token} with limit {limit}")

    # Fetch and cache total supply
    total_supply = await get_total_supply(token)
    if total_supply == 0:
        raise ValueError("Total supply is zero. Cannot calculate percentages.")

    # Fetch top holders
    top_holders =await get_top_holders(token, limit)
    print(f"Retrieved {len(top_holders)} holders for token {token}")
    token_overview = get_token_overview(token)
    if token_overview:
        token_overview = token_overview['data']
        symbol = token_overview['symbol']
        name = token_overview['name']
        logo_url = token_overview['logo_uri']
        liquidity = token_overview['liquidity']
        market_cap = token_overview['mc']
        #more info about the token
    else:
        token_overview = None
    token_info = {
        'symbol': symbol,
        'name': name,
        'logo_url': logo_url,
        'liquidity': liquidity,
        'market_cap': market_cap,
    }
    async with ClientSession() as session:
        results = [token_info]
        for i in range(0, len(top_holders), BATCH_SIZE):
            # Process holders in batches
            batch = top_holders[i:i + BATCH_SIZE]
            tasks = [
                process_holder(count, holder, session, total_supply, token)
                for count, holder in enumerate(batch, start=i + 1)
            ]
            results.extend(await asyncio.gather(*tasks))

            # Introduce a delay to respect the rate limit
            if i + BATCH_SIZE < len(top_holders):
                print("Waiting to respect API rate limit...")
                time.sleep(1)  # Wait 1 second before processing the next batch

    return results
def get_avg_top_holders_age(token:str=None, limit:int=50):
    """
    Get the average age of the top holders of a token
    Costs 50 credits per request
    """
    top_holders = get_top_holders(token, limit)
    ages = [get_wallet_age(holder['owner']) for holder in top_holders]
    return sum(ages) / len(ages)
async def get_wallet_portfolio(count, holder, session, total_supply, token):
    """
    Process a single holder with adaptive pacing.
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100
    portfolio = await fetch_wallet_portfolio(session, wallet)
    if "error" in portfolio:
        return {f'wallet {count}': portfolio}

    net_worth = round(portfolio['data']['total_usd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    for item in holdings:
        if item['address'] == token:
            net_worth_excluding = net_worth - item['value_usd']
            break  
        else:
            net_worth_excluding = net_worth

    # Get top holdings efficiently
    top_holdings = holdings[:3]
    return {
        f'wallet {count}': {
            'wallet': wallet,
            'amount': amount,
            'share_in_percent': round(share_in_percent, 3),
            'net_worth': net_worth,
            'net_worth_excluding': net_worth_excluding,
            'first_top_holding': top_holdings[0] if len(top_holdings) > 0 else None,
            'second_top_holding': top_holdings[1] if len(top_holdings) > 1 else None,
            'third_top_holding': top_holdings[2] if len(top_holdings) > 2 else None,
        }
    }
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
            value_usd = float(holder['ui_amount']) * price
            if value_usd >= min_value_usd:
                all_holders.append(holder)
            else:
                # Since holders are ordered by amount, we can stop once we hit one below threshold
                return all_holders
                
        offset += batch_size
        
    return all_holders




async def get_holding_distribution(token: str = None):
    """
    Get the holding distribution of a token.
    """
    if token is None:
        print("Token not provided.")
        return None

    consider_only_percent = 0.1

    # Fetch token overview
    token_overview = get_token_overview(token)  # Assuming this is a synchronous function
    if not token_overview or not token_overview.get('data'):
        print("Failed to fetch token overview.")
        return None

    holder_count = token_overview['data'].get('holder', 0)
    total_supply = token_overview['data'].get('mc', 0)
    print(f"Getting holding distribution for {token} with {holder_count} holders")

    # Fetch top holders
    top_holders = await get_top_holders(token, round(holder_count * consider_only_percent))
    if not top_holders:
        print("Failed to fetch top holders.")
        return None

    ranges = {
        "0-20": 0,
        "20-250": 0,
        "250-2000": 0,
        "2000-10000": 0,
        "10000+": 0,
    }

    semaphore = asyncio.Semaphore(15)  # Limit to 10 concurrent tasks

    async def process_holder(session, count, holder):
        print(f"Processing holder {holder['owner']}")
        async with semaphore:  # Ensure no more than 10 concurrent tasks
            try:
                portfolio = await get_wallet_portfolio(count, holder, session, total_supply, token)
                if "error" in portfolio:
                    print(f"Error in portfolio for wallet {holder['owner']}: {portfolio}")
                    return

                wallet_data = portfolio.get(f'wallet {count}')
                if not wallet_data:
                    print(f"No data returned for wallet {holder['owner']}")
                    return

                net_worth_excluding = wallet_data.get("net_worth_excluding")
                if net_worth_excluding is None:
                    print(f"Missing key 'value_usd' for holder {holder['owner']}. Skipping...")
                    return

                # Categorize net worth
                if net_worth_excluding < 20:
                    ranges["0-20"] += 1
                elif net_worth_excluding < 250:
                    ranges["20-250"] += 1
                elif net_worth_excluding < 2000:
                    ranges["250-2000"] += 1
                elif net_worth_excluding < 10000:
                    ranges["2000-10000"] += 1
                else:
                    ranges["10000+"] += 1
            except Exception as e:
                print(f"Error processing holder {holder['owner']}: {e}")

    async def process_all_holders():
        # Use batched processing to avoid creating too many tasks simultaneously
        batch_size = 10
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(top_holders), batch_size):
                tasks = [
                    process_holder(session, idx + 1, holder)
                    for idx, holder in enumerate(top_holders[i:i + batch_size])
                ]
                await asyncio.gather(*tasks)
                # Throttle to avoid exceeding API rate limits
                await asyncio.sleep(1)

    await process_all_holders()
    return [{k: v} for k, v in ranges.items()]

def get_balance(wallet:str, token:str=None):
    print("Getting balance for", wallet, "in", token)
    """
    Get the balance of a wallet in SOL or a token
    Costs 135 credits
    """	
    headers = {"Content-Type": "application/json"}
    if token:
        # Get token balance
        data = {
            "jsonrpc": "2.0",
            "method": "get_token_accounts_by_owner",
            "params": [
                wallet,
                {"mint": token},
                {"encoding": "json_parsed"}
            ],
            "id": 1
        }
        response = requests.post(heliusrpc, headers=headers, json=data)
        if response.status_code != 200:
            return None
        result = response.json().get('result', {}).get('value', [])
        if not result:
            return 0
        token_amount = float(result[0]['account']['data']['parsed']['info']['token_amount']['amount'])
        decimals = result[0]['account']['data']['parsed']['info']['token_amount']['decimals']
        return token_amount / (10 ** decimals)
    else:
        # Get SOL balance
        data = {
            "jsonrpc": "2.0", 
            "method": "get_balance",
            "params": [wallet],
            "id": 1
        }
        response = requests.post(get_rpc(), headers=headers, json=data)
        if response.status_code != 200:
            return None
            
        balance = response.json().get('result', {}).get('value', 0)
        return balance / (10 ** 9)  # Convert lamports to SOL
async def get_total_supply(token:str=None):
    print("Getting total supply for", token)
    """
    Get the total supply of a token
    Costs 0 credits per request
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "method": "get_token_supply",
        "params": [token],
        "id": 1
    }
    response = requests.post(get_rpc(), headers=headers, json=data)
    if response.status_code != 200:
        return None
    return float(response.json()['result']['value']['ui_amount'])
async def get_top_holders(token:str=None, limit = None):
    print("Getting top holders for", token, "with limit", limit)
    """
    Get the top holders of a token, costs 50 credits per request
    Iterates through all holders using offset pagination
    """	
    all_holders = []
    if token is None:
        return True

    offset = 0
    batch_size = 100 if limit is None or limit > 100 else limit
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
        if limit is None:
            offset += batch_size
        else:
            break
    return all_holders

def get_transaction_data(signature:str=None):
    print("Getting transaction data for", signature)
    """
    Get the data of a transaction
    Costs 50 credits per request
    """
    if signature is None:
        return None
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "jsonrpc": "2.0",
        "method": "get_transaction",
        "params": [signature, {'max_supported_transaction_version': 0}],
        "id": 1
    }
    response = requests.post(heliusrpc, headers=headers, json=data)
    if response.status_code != 200:
        return None
    return response.json()
semaphore = asyncio.Semaphore(10)

# Asynchronous request to fetch all signatures with retry logic
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

# Asynchronous request to fetch transaction data by Solscan
async def get_transaction_data_by_solscan(signature: str = None):
    print("Getting transaction data for", signature)
    """
    Get the data of a transaction by Solscan.
    Costs 50 credits per request.
    """
    if signature is None:
        return None
    headers = { 
        'token': solscanapi
    }
    url = f"https://pro-api.solscan.io/v2.0/transaction/detail?tx={signature}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None

# Asynchronous function to process fresh wallets
# async def get_holders_fresh_wallets_ready(token: str = None, limit: int = None):
#     print("Getting fresh wallets for", token, "with limit", limit)
#     """
#     Get the fresh wallets of the top holders of a token.
#     Costs 50 credits per request.
#     """
#     fresh_definition = 604800  # Fresh criteria: last activity in the last 7 days
#     top_holders = await get_top_holders(token, limit)
#     print("Applying Fresh Criteria on", len(top_holders), "holders")
#     result = []
#     count = 1
#     total_supply = await get_total_supply(token)
#     funder = None
#     funded = None
    
#     tasks = []
#     async with aiohttp.ClientSession() as session:
#         for holder in top_holders:
#             tasks.append(process_holder(session, holder, fresh_definition, total_supply, count))

#         results = await asyncio.gather(*tasks)
#         for res in results:
#             if res:  # Only append non-None results
#                 result.append(res)
    
#     return result

# # Helper asynchronous function to process each holder
# async def process_holder(session, holder, fresh_definition, total_supply, count):
#     time_now_in_unix = int(time.time())
#     AllSignatures = await get_all_signatures(holder['owner'], 5000)
    
#     if AllSignatures is None or len(AllSignatures) == 0:
#         print(f"Skipping {holder['owner']} due to missing signatures or empty result.")
#         return None

#     if len(AllSignatures) != 5000 and AllSignatures[-1]['block_time'] > time_now_in_unix - fresh_definition:
#         print(f"Considering {holder['owner']} because it is fresh")
#         wallet_age = get_wallet_age_readable(time_in_unix=AllSignatures[-1]['block_time'])
#         LastSignature = AllSignatures[-1]
#         last_tx = await get_transaction_data_by_solscan(LastSignature['signature'])
#         if not last_tx:
#             print(f"Skipping {holder['owner']} due to missing transaction data.")
#             return None
#         sol_bal_change = last_tx['data']['sol_bal_change']
#         funder = sol_bal_change[0]['address']
#         funded = abs(int(sol_bal_change[0]['change_amount'])) / 10**9
#         amount = holder['ui_amount']
#         share_in_percent = float(amount) / total_supply * 100
#         return {count: {"wallet": holder['owner'], "amount": amount, "share_in_percent": share_in_percent, "funder": funder, "funded": funded, "wallet_age": wallet_age, 'Signature': LastSignature['signature']}}
    
#     return None



def get_token_overview(token:str=None):
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
    return response.json()
def get_note_worthy_holders(token:str=None, limit:int=50):
    """
    Get the notable holders of a token
    Costs 50 credits per request
    """
    top_holders = get_top_holders(token, limit)
    token_overview = get_token_overview(token)
    symbol = token_overview['data']['symbol']
    price = token_overview['data']['price']
    mc = token_overview['data']['mc']
    liquidity = token_overview['data']['liquidity']
    holder = token_overview['data']['holder']

    result = []
    return result
if __name__ == "__main__":
    #print(get_price("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 1733364671))
    #print(asyncio.run(get_top_holders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 10)))
    #print(get_total_supply("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    #print(get_wallet_age("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii"))
    #print(get_balance("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    #print(get_wallet_portfolio("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF"))
    #print(get_top_holders_info("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 50))
    #print(get_wallet_age_readable("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii"))
    #print(get_wallet_age("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF"))
    #print(get_wallet_portfolio("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"))
    #print(get_wallet_age("5PAhQiYdLBd6SVdjzBQDxUAEFyDdF5ExNPQfcscnPRj5"))
    #print(get_avg_top_holders_age("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 50))
    #print(get_wallet_age("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"))
    #print(get_wallet_portfolio_excluding("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    #print((get_funding_source("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs")))
    # print(get_top_holders("BUXyVrRMvBU6EUY9rnqNv3JqUwsSxG9gpnRFVzMbpump"))
    # tx = get_transaction_data("PRpQD6GcMirjnA6vVuWDGGJLV3hZSferwWEF44FZfeJhUbicud2kSec5oF4KUQ3AhWZdnNWmteYaRXkFik1qQYY")
    # print(tx['result']['transaction']['message']['account_keys'])
    #print(get_holders_fresh_wallets("BUXyVrRMvBU6EUY9rnqNv3JqUwsSxG9gpnRFVzMbpump", 50))
    # print(get_token_overview("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    # print (0.0195 * get_total_supply("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    # top holders of a token displaying top 3 holdings of other tokens in the portfolio
    # fresh
    time_now_in_unix_miliseconds = int(time.time() * 1000)
    # print(get_wallet_age("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"))
    #print(asyncio.run(get_holders_fresh_wallets_ready("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump")))
    #print(get_token_overview("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump"))
    print(asyncio.run(get_top_holders_ready("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump", 35)))
   # print(asyncio.run(get_holding_distribution("9QZc9WPD2VctdscCxdotsKB4KaNQK6sozDq6kbJwpump")))
    #print(asyncio.run(get_top_holders_with_constraint("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 300000, 0.02)))
    print(((int(time.time() * 1000) - time_now_in_unix_miliseconds))/1000)
    #print(get_transaction_data(get_last_signature("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii")['signature']))
    #print(get_transaction_data("2734DGsm5wDYFU9w6ojYFrKJVehbE5nP56hLTokifU1qt6nftVASLp2d9i4UGTigErvLjFeySZdn294V5NCV6aWe"))
    #print((get_all_signatures("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", 5000)))
    #print(get_transaction_data_by_solscan("isQu5fMeaiQ2eN3fqrvDaTpPNjcTTcuiQkMEtowZvtNQj26zgycE3ofwHkPjowqUNgUUyuqdWZpQAgUd2nLiNzy"))
    #print(asyncio.run(get_top_holders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 5)))

 