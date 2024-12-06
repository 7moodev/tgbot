import os
import requests
import time
import base58


birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
def getTopHolders(token:str=None, limit:int=100):
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

def getWalletAge(wallet:str=None):
    """
    Get the blocktime of the oldest transaction of a wallet in unix time. 0 For exchanges
    """	
    if wallet is None:
        return None
    headers = {
        "Content-Type": "application/json",
    }
    all_signatures = []
    before = None
    while True:
        if len(all_signatures) > 1000:
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

def getBalance(wallet:str, token:str=None):
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

#print(getPrice("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 1733364671))
#print(getTopHolders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 10))
print(getWalletAge("FQRsxivsWpiRAw1uegTKshwjf8vaco2QgLKbz3vbepii"))
#print(getBalance("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
