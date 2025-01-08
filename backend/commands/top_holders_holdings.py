import os
import asyncio
import httpx
from .utils.token_utils import get_token_supply, get_token_overview, get_top_holders
from .utils.wallet_utils import get_wallet_age
import time
from aiohttp import ClientSession, ClientError



'''
TODO: Ready to integrate functions: get_top_holders_holdings(token, limit)
Inputs: 
    - str: token address
    - int: limit of top holders to retrieve
Outputs: an array of dictionaries containing:
    - dict: of the quered token info:
    {'symbol': 'OBOT', 'name': 'OBOT', 'logoURI': 'https://ipfs.io/ipfs/QmeeSqjjrpQ5ht5uc21uG3j3PdVM46CkfTXUCyt23vs462', 'liquidity': 1012943.0935280464, 'market_cap': 8515447.962210068}
    
    - array: dicts of total holders with their respective top holdings: 
    [{'count': 1, 'wallet': 'GczJXQD9Bap8EypqDn6RCoUqQruKZVs2pkQL3fUHeuZS', 'amount': 64679621.584084, 'share_in_percent':
    8.828, 'net_worth': 751769.4571355829, 'net_worth_excluding': 0.597090429160744,
    'first_top_holding': {'address': '7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump',
    'decimals': 6, 'balance': 64679621584084, 'uiAmount': 64679621.584084, 'chainId': 'solana',
    'name': 'OBOT', 'symbol': 'OBOT', 'icon': 'https://ipfs.io/ipfs/QmeeSqjjrpQ5ht5uc21uG3j3PdVM46CkfTXUCyt23vs462',
    'logoURI': 'https://ipfs.io/ipfs/QmeeSqjjrpQ5ht5uc21uG3j3PdVM46CkfTXUCyt23vs462', 'priceUsd': 0.011622963178098508,
    'valueUsd': 751768.8600451538}, 'second_top_holding': {'address': 'So11111111111111111111111111111111111111111',
    'decimals': 9, 'balance': 2951040, 'uiAmount': 0.00295104, 'chainId': 'solana', 'name': 'SOL', 'symbol': 'SOL',
    'logoURI': 'https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png',
      'priceUsd': 202.33220464636622,
      'valueUsd': 0.5970904291996125}, 'third_top_holding': 0}, {'count': 2...}]
'''
# Fetch API key from environment variables
birdeyeapi = os.environ.get('birdeyeapi')
API_RATE_LIMIT = 15  # Max API calls per second
BATCH_SIZE = 15  # Maximum requests allowed per batch (aligned with rate limit)

async def fetch_wallet_portfolio(session, wallet: str):
    print(f"Fetching portfolio for wallet {wallet}")
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
        print(f"Fetched portfolio for wallet {wallet}")
        return data

async def process_holder1(count, holder, session, total_supply, token):
    print(f"Processing holder {count} with wallet {holder['owner']}")
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
    print(f"Processed holder {count} with wallet {wallet}")
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

async def get_top_holders_unready(token: str = None, limit: int = 50):
    print(f"Getting top holders info for {token} with limit {limit}")
    """
    Get the info of the top holders of a token with adaptive pacing for API requests.
    """
    if token is None:
        return None
    # Fetch and cache total supply
    total_supply = await get_token_supply(token)
    if total_supply == 0:
        raise ValueError("Total supply is zero. Cannot calculate percentages.")

    # Fetch top holders
    top_holders =await get_top_holders(token, limit)
    print(f"Retrieved {len(top_holders)} holders for token {token}")
    token_overview = await get_token_overview(token)
    if token_overview:
        token_overview = token_overview['data']
        symbol = token_overview['symbol']
        name = token_overview['name']
        logo_url = token_overview['logoURI']
        liquidity = token_overview['liquidity']
        market_cap = token_overview['mc']
        #more info about the token
    else:
        token_overview = None
    token_info = {
        'symbol': symbol,
        'name': name,
        'logoURI': logo_url,
        'liquidity': liquidity,
        'market_cap': market_cap,
    }
    async with ClientSession() as session:
        results = [token_info]
        for i in range(0, len(top_holders), BATCH_SIZE):
            # Process holders in batches
            batch = top_holders[i:i + BATCH_SIZE]
            tasks = [
                process_holder1(count, holder, session, total_supply, token)
                for count, holder in enumerate(batch, start=i + 1)
            ]
            results.extend(await asyncio.gather(*tasks))

            # Introduce a delay to respect the rate limit
            if i + BATCH_SIZE < len(top_holders):
                print("Resumed processing")
    print("Finished processing all holders")
    return results

async def get_wallet_portfolio(wallet: str):
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:  # Changed from status to status_code
        return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
    data = response.json()['data']
    if not data.get('success', True):
        return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
    return data
import asyncio
import httpx
from typing import List, Dict, Any

# Semaphore to limit concurrent requests to 15 per second
REQUEST_SEMAPHORE = asyncio.Semaphore(10)

async def get_wallet_portfolio(wallet: str, session: httpx.AsyncClient):
    """
    Fetch wallet portfolio with rate limiting and error handling
    
    :param wallet: Wallet address to fetch portfolio for
    :param session: Shared HTTP client session
    :return: Portfolio data or error dict
    """
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi  # Assumes birdeyeapi is defined elsewhere
    }
    async with REQUEST_SEMAPHORE:
        try:
            response = await session.get(url, headers=headers)
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
            
            data = response.json()['data']
            
            if not data.get('success', True):
                return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
            
            return data
        except Exception as e:
            return {"error": f"Exception fetching portfolio for wallet {wallet}: {str(e)}"}

def extract_holding_excluding(portfolio: Dict[str, Any], token: str) -> float:
    """
    Extract total portfolio value excluding a specific token
    
    :param portfolio: Wallet portfolio data
    :param token: Token address to exclude
    :return: Portfolio value excluding specified token
    """
    for holding in portfolio['items']:
        if holding['address'] == token:
            return portfolio['totalUsd'] - holding['valueUsd']
    return 0

async def process_holder(
    count: int,
    holder: Dict[str, Any], 
    token: str, 
    total_supply: float, 
    session: httpx.AsyncClient
) -> Dict[str, Any]:

    """
    Process a single token holder's information
    
    :param holder: Holder information dictionary
    :param token: Token address
    :param total_supply: Total token supply
    :param session: Shared HTTP client session
    :return: Processed holder information
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100
    
    # Fetch wallet portfolio
    portfolio = await get_wallet_portfolio(wallet, session)
    
    # If there's an error, return error information
    if "error" in portfolio:
        return {
            'wallet': wallet, 
            'error': portfolio.get('error', 'Unknown error')
        }
    
    # Process portfolio details
    net_worth = portfolio.get('totalUsd', 0)
    
    # Safely extract top holdings
    try:
        first_top_holding = portfolio['items'][0] if portfolio['items'] else 0
    except:
        first_top_holding = 0
    try:    
        second_top_holding = portfolio['items'][1] if len(portfolio['items']) > 1 else 0
    except:
        second_top_holding = 0
    try:
        third_top_holding = portfolio['items'][2] if len(portfolio['items']) > 2 else 0
    except:
        third_top_holding = 0
    
    return {
        'count': count,
        'wallet': wallet,
        'amount': amount,
        'share_in_percent': round(share_in_percent, 3),
        'net_worth': net_worth,
        'net_worth_excluding': extract_holding_excluding(portfolio, token),
        'first_top_holding': first_top_holding,
        'second_top_holding': second_top_holding,
        'third_top_holding': third_top_holding,
        #potential to add wallet age
    }

async def get_top_holders_holdings(
    token: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get top token holders with concurrent processing
    
    :param token: Token address
    :param limit: Number of top holders to process
    :return: List of processed holder information
    """
    # These functions are assumed to be defined elsewhere in your code
    total_supply = await get_token_supply(token)
    top_holders = await get_top_holders(token, limit)
    
    # Fetch token overview
    token_overview = await get_token_overview(token)
    if token_overview:
        token_overview = token_overview['data']
        token_info = {
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview['logoURI'],
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['mc'],
        }
    else:
        token_info = {}
    
    # Create a single HTTP client session for all requests
    async with httpx.AsyncClient() as session:
        # Use asyncio.gather to process holders concurrently
        holder_tasks = [
            process_holder(count, holder, token, total_supply, session) 
            for count, holder in enumerate(top_holders, start=1)
        ]
        
        # Wait for all holder processing to complete
        processed_holders = await asyncio.gather(*holder_tasks)
    
    # Combine results
    
    return token_info, processed_holders





def format_message(token_info, top_holders):

    # Token information part
    message = f"**Token Info**: {token_info['symbol']} ({token_info['name']})\n"
    message += f"├── MC: ${token_info['market_cap'] / 1e6:.2f}M\n"
    message += f"├── Liquidity: ${token_info['liquidity']:.2f}\n\n"
    # message += f"├── Holders count: {token_info['holders']}\n"
    message += f"**Holdings of the top {len(top_holders)}:**\n\n"
    # Top holders part
    for holder in top_holders:
        if "error" in holder:
            continue
        message += f"#{holder['count']}- ({shorten_address(holder['wallet'])}) (💰NW_Excl:{holder["net_worth"]} |"
        top1 = holder["first_top_holding"]
        top2 = holder["second_top_holding"]
        top3 = holder["third_top_holding"]
        if top1:
            message += f"🥇{top1['symbol']}({top1['valueUsd']})"
        if top2:
            message += f"🥈{top2['symbol']}({top2['valueUsd']})"
        if top3:
            message += f"🥉{top3['symbol']}({top3['valueUsd']})"
    return message


def shorten_address(address: str, length: int = 4) -> str:
    """
    Shorten the address to the given length.
    """
    return f"{address[:length]}...{address[-length:]}"
# # Convert to the readable format
# if __name__ == "__main__":
#     token_info, top_holders = asyncio.run(get_top_holders_holdings("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", 5))
#     formatted_message = format_message(token_info=token_info, top_holders=top_holders)
#     print(formatted_message)
#     #print(shorten_address("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"))
if __name__ == "__main__":
    timenow = float(time.time())
    holders = asyncio.run(get_top_holders_holdings("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump",30))
    print(holders)
    #print(format_message(holders[0], holders[1]))
    #print(asyncio.run(get_wallet_portfolio("GitBH362uaPmp5yt5rNoPQ6FzS2t7oUBqeyodFPJSZ84")))
    print(float(time.time()) - timenow)


