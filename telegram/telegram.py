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
from img import draw
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

def getRpc():
    Random = random.randint(0, 1)
    if Random == 0:
        print("Using heliusrpc")
        return heliusrpc
    else:
        print("Using quicknoderpc")
        return quicknoderpc

def getPrice(token:str=None, unixTime:int = None):
    print("Getting price for", token, "at", unixTime)
    """
    Get the price of a token at a given unix time, costs 5 credits per request
    """		
    if unixTime is None:
        unixTime = int(time.time())
    if token is None:
        token = "So11111111111111111111111111111111111111112"
    url = f"https://public-api.birdeye.so/defi/historical_price_unix?address={token}&unixtime={unixTime}"
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
def getWalletAgeReadable(wallet:str=None, timeInUnix=None):
    if timeInUnix is None:
        walletAgeUnix = getWalletAge(wallet)
    else:
        walletAgeUnix = timeInUnix
    if walletAgeUnix == 0:
        return 'Exchange/LP'
    if walletAgeUnix is None:
        return None
    current_time = int(time.time())
    age_seconds = current_time - walletAgeUnix
    
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
def getWalletAge(wallet:str=None,  maxSignatures:int=MAX_SIGNATURES, botFilter:bool=True):
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
        timeNowinUnix = int(time.time())
        if all_signatures:
            botCheck = botFilter and timeNowinUnix - all_signatures[-1].get('blockTime') < 36000
        else:
            botCheck = False
        if len(all_signatures) > maxSignatures or botCheck:
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
        response = requests.post(getRpc(), headers=headers, json=data)
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
        return all_signatures[-1].get('blockTime')
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
    net_worth = round(portfolio['data']['totalUsd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    token_item = next((item for item in holdings if item['address'] == token), None)
    net_worth_excluding = net_worth - (token_item['valueUsd'] if token_item else 0)
    # Get top holdings efficiently
    top_holdings = holdings[:3]
    
    return {
            f'wallet {count}': {
                'wallet': wallet,
                'amount': amount,
                'shareInPercent': round(share_in_percent, 3),
                'netWorth': net_worth,
                'netWorthExcluding': net_worth_excluding,
                'firstTopHolding': top_holdings[0] if len(top_holdings) > 0 else None,
                'secondTopHolding': top_holdings[1] if len(top_holdings) > 1 else None,
                'thirdTopHolding': top_holdings[2] if len(top_holdings) > 2 else None,
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
    total_supply = await getTotalSupply(token)
    if total_supply == 0:
        raise ValueError("Total supply is zero. Cannot calculate percentages.")

    # Fetch top holders
    top_holders =await getTopHolders(token, limit)
    print(f"Retrieved {len(top_holders)} holders for token {token}")
    tokenOverview = getTokenOverview(token)
    if tokenOverview:
        tokenOverview = tokenOverview['data']
        symbol = tokenOverview['symbol']
        name = tokenOverview['name']
        logoUrl = tokenOverview['logoURI']
        liquidity = tokenOverview['liquidity']
        marketCap = tokenOverview['mc']
        #more info about the token
    else:
        tokenOverview = None
    token_info = {
        'symbol': symbol,
        'name': name,
        'logoUrl': logoUrl,
        'liquidity': liquidity,
        'marketCap': marketCap,
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
    draw(results)
    return results
def getAvgTopHoldersAge(token:str=None, limit:int=50):
    """
    Get the average age of the top holders of a token
    Costs 50 credits per request
    """
    topHolders = getTopHolders(token, limit)
    ages = [getWalletAge(holder['owner']) for holder in topHolders]
    return sum(ages) / len(ages)
async def getWalletPortfolio(count, holder, session, total_supply, token):
    """
    Process a single holder with adaptive pacing.
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100
    portfolio = await fetch_wallet_portfolio(session, wallet)
    if "error" in portfolio:
        return {f'wallet {count}': portfolio}

    net_worth = round(portfolio['data']['totalUsd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    for item in holdings:
        if item['address'] == token:
            net_worth_excluding = net_worth - item['valueUsd']
            break  
        else:
            net_worth_excluding = net_worth

    # Get top holdings efficiently
    top_holdings = holdings[:3]
    return {
        f'wallet {count}': {
            'wallet': wallet,
            'amount': amount,
            'shareInPercent': round(share_in_percent, 3),
            'netWorth': net_worth,
            'netWorthExcluding': net_worth_excluding,
            'firstTopHolding': top_holdings[0] if len(top_holdings) > 0 else None,
            'secondTopHolding': top_holdings[1] if len(top_holdings) > 1 else None,
            'thirdTopHolding': top_holdings[2] if len(top_holdings) > 2 else None,
        }
    }
async def getTopHoldersWithConstraint(token:str=None, min_value_usd:float=None, price:float=None):
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























async def getHoldingDistribution(token: str = None):
    """
    Get the holding distribution of a token.
    """
    if token is None:
        print("Token not provided.")
        return None

    considerOnlyPercent = 0.1

    # Fetch token overview
    tokenOverview = getTokenOverview(token)  # Assuming this is a synchronous function
    if not tokenOverview or not tokenOverview.get('data'):
        print("Failed to fetch token overview.")
        return None

    holder_count = tokenOverview['data'].get('holder', 0)
    total_supply = tokenOverview['data'].get('mc', 0)
    print(f"Getting holding distribution for {token} with {holder_count} holders")

    # Fetch top holders
    topHolders = await getTopHolders(token, round(holder_count * considerOnlyPercent))
    if not topHolders:
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
                portfolio = await getWalletPortfolio(count, holder, session, total_supply, token)
                if "error" in portfolio:
                    print(f"Error in portfolio for wallet {holder['owner']}: {portfolio}")
                    return

                wallet_data = portfolio.get(f'wallet {count}')
                if not wallet_data:
                    print(f"No data returned for wallet {holder['owner']}")
                    return

                net_worth_excluding = wallet_data.get("netWorthExcluding")
                if net_worth_excluding is None:
                    print(f"Missing key 'valueUsd' for holder {holder['owner']}. Skipping...")
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
            for i in range(0, len(topHolders), batch_size):
                tasks = [
                    process_holder(session, idx + 1, holder)
                    for idx, holder in enumerate(topHolders[i:i + batch_size])
                ]
                await asyncio.gather(*tasks)
                # Throttle to avoid exceeding API rate limits
                await asyncio.sleep(1)

    await process_all_holders()
    return [{k: v} for k, v in ranges.items()]

def getBalance(wallet:str, token:str=None):
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
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet,
                {"mint": token},
                {"encoding": "jsonParsed"}
            ],
            "id": 1
        }
        response = requests.post(heliusrpc, headers=headers, json=data)
        if response.status_code != 200:
            return None
        result = response.json().get('result', {}).get('value', [])
        if not result:
            return 0
        token_amount = float(result[0]['account']['data']['parsed']['info']['tokenAmount']['amount'])
        decimals = result[0]['account']['data']['parsed']['info']['tokenAmount']['decimals']
        return token_amount / (10 ** decimals)
    else:
        # Get SOL balance
        data = {
            "jsonrpc": "2.0", 
            "method": "getBalance",
            "params": [wallet],
            "id": 1
        }
        response = requests.post(getRpc(), headers=headers, json=data)
        if response.status_code != 200:
            return None
            
        balance = response.json().get('result', {}).get('value', 0)
        return balance / (10 ** 9)  # Convert lamports to SOL
async def getTotalSupply(token:str=None):
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
    response = requests.post(getRpc(), headers=headers, json=data)
    if response.status_code != 200:
        return None
    return float(response.json()['result']['value']['uiAmount'])
async def getTopHolders(token:str=None, limit = None):
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

def getTransactionData(signature:str=None):
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
        "method": "getTransaction",
        "params": [signature, {'maxSupportedTransactionVersion': 0}],
        "id": 1
    }
    response = requests.post(heliusrpc, headers=headers, json=data)
    if response.status_code != 200:
        return None
    return response.json()
semaphore = asyncio.Semaphore(10)

# Asynchronous request to fetch all signatures with retry logic
async def getAllSignatures(wallet: str = None, limit: int = None):
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
                            "method": "getSignaturesForAddress",
                            "params": [wallet, {"limit": 1000, "before": before} if before else {"limit": 1000}],
                            "id": 1
                        }
                        async with session.post(getRpc(), headers=headers, json=data) as response:
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
async def getTransactionDataBySolscan(signature: str = None):
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
# async def getHoldersFreshWalletsReady(token: str = None, limit: int = None):
#     print("Getting fresh wallets for", token, "with limit", limit)
#     """
#     Get the fresh wallets of the top holders of a token.
#     Costs 50 credits per request.
#     """
#     freshDefinition = 604800  # Fresh criteria: last activity in the last 7 days
#     topHolders = await getTopHolders(token, limit)
#     print("Applying Fresh Criteria on", len(topHolders), "holders")
#     result = []
#     count = 1
#     totalSupply = await getTotalSupply(token)
#     funder = None
#     funded = None
    
#     tasks = []
#     async with aiohttp.ClientSession() as session:
#         for holder in topHolders:
#             tasks.append(process_holder(session, holder, freshDefinition, totalSupply, count))

#         results = await asyncio.gather(*tasks)
#         for res in results:
#             if res:  # Only append non-None results
#                 result.append(res)
    
#     return result

# # Helper asynchronous function to process each holder
# async def process_holder(session, holder, freshDefinition, totalSupply, count):
#     timeNowInUnix = int(time.time())
#     AllSignatures = await getAllSignatures(holder['owner'], 5000)
    
#     if AllSignatures is None or len(AllSignatures) == 0:
#         print(f"Skipping {holder['owner']} due to missing signatures or empty result.")
#         return None

#     if len(AllSignatures) != 5000 and AllSignatures[-1]['blockTime'] > timeNowInUnix - freshDefinition:
#         print(f"Considering {holder['owner']} because it is fresh")
#         walletAge = getWalletAgeReadable(timeInUnix=AllSignatures[-1]['blockTime'])
#         LastSignature = AllSignatures[-1]
#         lastTx = await getTransactionDataBySolscan(LastSignature['signature'])
#         if not lastTx:
#             print(f"Skipping {holder['owner']} due to missing transaction data.")
#             return None
#         sol_bal_change = lastTx['data']['sol_bal_change']
#         funder = sol_bal_change[0]['address']
#         funded = abs(int(sol_bal_change[0]['change_amount'])) / 10**9
#         amount = holder['ui_amount']
#         shareInPercent = float(amount) / totalSupply * 100
#         return {count: {"wallet": holder['owner'], "amount": amount, "shareInPercent": shareInPercent, "funder": funder, "funded": funded, "walletAge": walletAge, 'Signature': LastSignature['signature']}}
    
#     return None



def getTokenOverview(token:str=None):
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
def getNoteWorthyHolders(token:str=None, limit:int=50):
    """
    Get the notable holders of a token
    Costs 50 credits per request
    """
    topHolders = getTopHolders(token, limit)
    tokenOverview = getTokenOverview(token)
    symbol = tokenOverview['data']['symbol']
    price = tokenOverview['data']['price']
    mc = tokenOverview['data']['mc']
    liquidity = tokenOverview['data']['liquidity']
    holder = tokenOverview['data']['holder']

    result = []
    return result
if __name__ == "__main__":
    #print(getPrice("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 1733364671))
    #print(asyncio.run(getTopHolders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 10)))
    #print(getTotalSupply("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    #print(getWalletAge("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii"))
    #print(getBalance("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    #print(getWalletPortfolio("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF"))
    #print(getTopHoldersInfo("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 50))
    #print(getWalletAgeReadable("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii"))
    #print(getWalletAge("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF"))
    #print(getWalletPortfolio("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"))
    #print(getWalletAge("5PAhQiYdLBd6SVdjzBQDxUAEFyDdF5ExNPQfcscnPRj5"))
    #print(getAvgTopHoldersAge("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 50))
    #print(getWalletAge("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"))
    #print(getWalletPortfolioExcluding("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    #print((getFundingSource("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs")))
    # print(getTopHolders("BUXyVrRMvBU6EUY9rnqNv3JqUwsSxG9gpnRFVzMbpump"))
    # tx = getTransactionData("PRpQD6GcMirjnA6vVuWDGGJLV3hZSferwWEF44FZfeJhUbicud2kSec5oF4KUQ3AhWZdnNWmteYaRXkFik1qQYY")
    # print(tx['result']['transaction']['message']['accountKeys'])
    #print(getHoldersFreshWallets("BUXyVrRMvBU6EUY9rnqNv3JqUwsSxG9gpnRFVzMbpump", 50))
    # print(getTokenOverview("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    # print (0.0195 * getTotalSupply("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"))
    # top holders of a token displaying top 3 holdings of other tokens in the portfolio
    # fresh
    timeNowInUnixMiliseconds = int(time.time() * 1000)
    # print(getWalletAge("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"))
    #print(asyncio.run(getHoldersFreshWalletsReady("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump")))
    #print(getTokenOverview("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump"))
    # print(asyncio.run(get_top_holders_ready("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump", 5)))
   # print(asyncio.run(getHoldingDistribution("9QZc9WPD2VctdscCxdotsKB4KaNQK6sozDq6kbJwpump")))
    print(asyncio.run(getTopHoldersWithConstraint("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 300000, 0.02)))
    print(((int(time.time() * 1000) - timeNowInUnixMiliseconds))/1000)
    #print(getTransactionData(getLastSignature("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii")['signature']))
    #print(getTransactionData("2734DGsm5wDYFU9w6ojYFrKJVehbE5nP56hLTokifU1qt6nftVASLp2d9i4UGTigErvLjFeySZdn294V5NCV6aWe"))
    #print((getAllSignatures("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", 5000)))
    #print(getTransactionDataBySolscan("isQu5fMeaiQ2eN3fqrvDaTpPNjcTTcuiQkMEtowZvtNQj26zgycE3ofwHkPjowqUNgUUyuqdWZpQAgUd2nLiNzy"))
    print(asyncio.run(getTopHolders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 5)))

 