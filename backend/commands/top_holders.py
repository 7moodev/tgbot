import os
import asyncio
import httpx
from munk.backend.utils.token_utils import get_token_total_supply, get_token_overview, get_top_holders
import time
from aiohttp import ClientSession, ClientError
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

async def process_holder(count, holder, session, total_supply, token):
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
    net_worth = round(portfolio['data']['total_usd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    token_item = next((item for item in holdings if item['address'] == token), None)
    net_worth_excluding = net_worth - (token_item['value_usd'] if token_item else 0)
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

async def get_top_holders_ready(token: str = None, limit: int = 50):
    print(f"Getting top holders info for {token} with limit {limit}")
    """
    Get the info of the top holders of a token with adaptive pacing for API requests.
    """
    if token is None:
        return None
    # Fetch and cache total supply
    total_supply = await get_token_total_supply(token)
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
            return portfolio['total_usd'] - holding['value_usd']
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
    net_worth = portfolio.get('total_usd', 0)
    
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
    }

async def getTopHoldersReady1(
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
    total_supply = await get_token_total_supply(token)
    top_holders = await get_top_holders(token, limit)
    
    # Fetch token overview
    token_overview = await get_token_overview(token)
    if token_overview:
        token_overview = token_overview['data']
        token_info = {
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logo_url': token_overview['logo_uri'],
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
    results = [token_info] + processed_holders
    
    return results

if __name__ == "__main__":
    timenow = float(time.time())
    print(asyncio.run(getTopHoldersReady1("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump",30)))
    #print(asyncio.run(get_wallet_portfolio("GitBH362uaPmp5yt5rNoPQ6FzS2t7oUBqeyodFPJSZ84")))
    print(float(time.time()) - timenow)


