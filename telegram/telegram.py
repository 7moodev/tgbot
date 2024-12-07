import os
import requests
import time
import base58
import functools


birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
MAX_SIGNATURES = 5000

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

def getTopHolders(token:str=None, limit:int=50):
    print("Getting top holders for", token, "with limit", limit)
    """
    Get the top holders of a token, costs 50 credits per request
    """	
    if limit > 100:
        limit = 100 #for now
    if token is None:
        return None
    url = f"https://public-api.birdeye.so/defi/v3/token/holder?address={token}&offset=0&limit={limit}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        if response.json()['success'] == False:
            return None
    return response.json()['data']['items']
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
def getWalletAgeReadable(wallet:str=None):
    walletAgeUnix = getWalletAge(wallet)
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
def getWalletAge(wallet:str=None):
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
    timeNowinUnix = int(time.time())
    while True:
        if all_signatures:  
            if len(all_signatures) > MAX_SIGNATURES or  all_signatures[-1].get('blockTime') < timeNowinUnix - 86400:
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
        response = requests.post(heliusrpc, headers=headers, json=data)
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
@timing_decorator
def getWalletPortfolio(wallet:str=None):
    print("Getting wallet portfolio for", wallet)
    """
    Get the portfolio of a wallet
    Costs 50 credits per request
    """
    if wallet is None:
        return None
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None
    if response.json()['success'] == False:
        return None
    return response.json()['data']['totalUsd']
    
def getTopHoldersInfo(token:str=None, limit:int=50):
    print("Getting top holders info for", token, "with limit", limit)
    """
    Get the info of the top holders of a token
    Costs 50 credits per request
    """
    if token is None:
        return None
    result = []
    topHolders = getTopHolders(token, limit)
    count = 1
    print(len(topHolders))
    for holder in topHolders:
        print("Processing holder", holder['owner'])
        shareInPercent = float(holder['ui_amount']) / getTotalSupply(token) * 100
        age = getWalletAgeReadable(holder['owner'])
        if age == 'Exchange/LP':
            netWorth = '>$1M'
        else:
            netWorth = round(getWalletPortfolio(holder['owner']),0)
        amount = holder['ui_amount']
        wallet = holder['owner']
        result.append({f'wallet {count}':{'wallet':wallet, 'amount':amount, 'shareInPercent':round(shareInPercent, 3), 'netWorth':netWorth, 'age':age}})
        count += 1
    return result

def getBalance(wallet:str, token:str=None):
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
        response = requests.post(heliusrpc, headers=headers, json=data)
        if response.status_code != 200:
            return None
            
        balance = response.json().get('result', {}).get('value', 0)
        return balance / (10 ** 9)  # Convert lamports to SOL
def getTotalSupply(token:str=None):
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
    response = requests.post(heliusrpc, headers=headers, json=data)
    if response.status_code != 200:
        return None
    return float(response.json()['result']['value']['uiAmount'])

