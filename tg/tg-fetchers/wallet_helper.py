
from utils import getRpc
import requests
import os
from token_helper import getTokenOverview, getPrice
birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
solscanapi = os.environ.get('solscan')



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
        response = requests.post(getRpc(), headers=headers, json=data)
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
def getWalletAvgPrice(wallet:str, token:str=None, side:str=None):
    """
    Get the average buy price of a token for a given wallet
    """
    defiActivityTypes = ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"]
    walletTradeHistory = getWalletTradeHistory(wallet, token, defiActivityTypes)
    print(walletTradeHistory)
    if walletTradeHistory:
        TradeSizeXPriceSum = 0
        TradeSizeSum = 0
        if walletTradeHistory['data']:
            for activity in walletTradeHistory['data']:
                blockTime = activity['block_time']
                price = getPrice(token, blockTime)
                if price:
                    routers = activity['routers']
                    if side == "buy":
                        if routers['token2'] == token:
                            TradeSizeXPriceSum += price * (routers['amount2'] / 10 ** 6)
                            TradeSizeSum += routers['amount2'] / 10 ** 6
                    elif side == "sell":
                        if routers['token1'] == token:
                            TradeSizeXPriceSum += price * (routers['amount1'] / 10 ** 6)
                            TradeSizeSum += routers['amount1'] / 10 ** 6
        try:
            return TradeSizeXPriceSum / TradeSizeSum
        except:
            return None
    return None
    
def getWalletTradeHistory(wallet:str, token:str=None, activityType:list[str]=None):
    """
    Get the average buy price of a token for a given wallet
    """
    base_url = f"https://pro-api.solscan.io/v2.0/account/defi/activities?address={wallet}"
    headers = {"token": solscanapi}
    if token:
        base_url += f"&token={token}"
    if activityType:
        for activity in activityType:
            base_url += f"&activity_type[]={activity}"
    response = requests.get(base_url, headers=headers)
    return response.json()
if __name__ == "__main__":
    print(getWalletAvgPrice("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF", "7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", "buy"))

