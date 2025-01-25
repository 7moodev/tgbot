import os
import asyncio
import httpx
from .utils.token_utils import get_token_supply, get_token_overview, get_top_holders, get_token_creation_info
from .utils.wallet_utils import get_wallet_age
import time
from aiohttp import ClientSession, ClientError
import json
import asyncio
import httpx
from typing import List, Dict, Any
birdeyeapi = os.environ.get('birdeyeapi')
API_RATE_LIMIT = 15  # Max API calls per second
BATCH_SIZE = 15  # Maximum requests allowed per batch (aligned with rate limit)
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
            print(f"Fetched portfolio for wallet {wallet}")
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
    
    top_holders = await get_top_holders(token, limit)
    token_creation_info = await get_token_creation_info(token)
    # Fetch token overview
    token_overview = await get_token_overview(token)
    total_supply = 0
    if token_overview:
        token_overview = token_overview['data']
        token_supply = token_overview['supply']
        token_info = {
            'price': token_overview['price'],
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview['logoURI'],
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['mc'],
            'supply': token_supply,
            'circulatingSupply': token_overview['circulatingSupply'],
            'realMc': token_overview['realMc'],
            'holder': token_overview['holder'],
            'extensions': token_overview['extensions'],
            'priceChange1hPercent': token_overview['priceChange1hPercent'],
            'creationTime': token_creation_info['blockUnixTime'],
        }
    else:
        token_info = {}
        token_supply = await get_token_supply(token)
    
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
    with open("backend/commands/outputs/top_holders_holdings.json", 'w') as f:
        json.dump({"token_info": token_info, "items": processed_holders}, f, indent=4)
    return {"token_info": token_info,"items": processed_holders}





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
        message += f"#{holder['count']}- ({shorten_address(holder['wallet'])}) (💰NW_Excl:{holder['net_worth']} |"
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
    holders = asyncio.run(get_top_holders_holdings("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump",10))
    print(holders)
    #print(format_message(holders[0], holders[1]))
    #print(asyncio.run(get_wallet_portfolio("GitBH362uaPmp5yt5rNoPQ6FzS2t7oUBqeyodFPJSZ84")))
    print(float(time.time()) - timenow)
    with open("backend/commands/outputs/top_holders_holdings.json", 'w') as f:
        json.dump(holders, f, indent=4)


