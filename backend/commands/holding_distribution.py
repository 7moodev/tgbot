import asyncio
import time
import json
import aiohttp
from asyncio import Semaphore
from aiohttp import ClientSession
import math
import os
from .utils.token_utils import get_token_overview, get_top_holders
from .utils.general_utils import get_whales


'''
TODO: Ready to integrate functions: get_holding_distribution(token)
Inputs: 
    - str: token address
Outputs: an array of dictionaries containing:
    - dictionary of the percentage of holders with different net worth ranges
    - dictionary of total holder count as well as total holders retrieved and processed
Example output:
[{'0-500': 72.0, '500-1000': 2.0, '1000-5000': 6.0, '5000-25000': 2.0, '25000+': 18.0}, {'holder_count': 7199, 'retrieved_holders': 50, 'Symbol': 'Mizuki', 'Name': 'Mizuki'}, {'symbol': 'Mizuki', 'name': 'Mizuki', 'logo_url': 'https://ipfs.io/ipfs/Qmdtq5b4Z5JouWWothvSXydP3Rz8WyqTKtQVXhh5LiZrrR', 'liquidity': 828098.4949007538, 'market_cap': 18011571.94138404}]
'''


api_key = os.environ.get('birdeyeapi')
# Example API rate limit: 900 requests per minute or 15 per second
API_RATE_LIMIT_PER_SECOND = 15
API_RATE_LIMIT_PER_MINUTE = 900
TOP_HOLDERS_TO_CONSIDER = 50
#tested benchmarks: 100 holders in 10.3 seconds, 80 holders in 8.3 seconds, 50 holders in 5.6 seconds

# Semaphore for limiting concurrent requests
semaphore = Semaphore(API_RATE_LIMIT_PER_SECOND)

# Async function to simulate fetching wallet portfolio
async def fetch_wallet_portfolio(session, wallet: str, api_key: str):
    """
    Asynchronously fetch wallet portfolio while respecting API rate limits.
    """
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": api_key
    }
    
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        data = await response.json()
        if not data.get('success', True):
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        return data

# Function to process a single holder
async def process_holder(session, count, holder, total_supply, token, ranges):
    """
    Process a single holder with adaptive pacing and rate limiting.
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100
    
    # Respect API rate limit by using the semaphore
    whales = await get_whales()
    async with semaphore:
        if wallet in whales:  # Skip whales
            ranges["25000+"] += 1
            return
        
        try:
            portfolio = await fetch_wallet_portfolio(session, wallet, api_key)
            if "error" in portfolio:
                print(f"Error fetching portfolio for wallet {wallet}")
                return
            
            net_worth = round(portfolio['data']['totalUsd'], 0)
            holdings = portfolio['data']['items']
            for item in holdings:
                if item['address'] == token:
                    net_worth_excluding = net_worth - item['valueUsd']
                    break
            else:
                net_worth_excluding = net_worth
            
            # Categorize net worth
            if net_worth_excluding < 500:
                ranges["0-500"] += 1
            elif net_worth_excluding < 1000:
                ranges["500-1000"] += 1
            elif net_worth_excluding < 5000:
                ranges["1000-5000"] += 1
            elif net_worth_excluding < 25000:
                ranges["5000-25000"] += 1
            else:
                ranges["25000+"] += 1
            
        except Exception as e:
            print(f"Error processing wallet {wallet}: {e}")

# Function to process all holders
async def process_all_holders(top_holders, total_supply, token):
    """
    Process all holders with a dynamic sleep to throttle the rate of requests.
    """
    ranges = {
        "0-500": 0,
        "500-1000": 0,
        "1000-5000": 0,
        "5000-25000": 0,
        "25000+": 0,
    }
    
    # Use batched processing to avoid creating too many tasks simultaneously
    batch_size = 15  # Max batch size based on the API limit
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(top_holders), batch_size):
            tasks = [
                process_holder(session, idx + 1, holder, total_supply, token, ranges)
                for idx, holder in enumerate(top_holders[i:i + batch_size])
            ]
            await asyncio.gather(*tasks)
            # Sleep dynamically to maintain the rate limit (15 requests per second)
            await asyncio.sleep(1)  # Sleep for a second after each batch of requests
            
    return ranges

# Function to get the holding distribution of a token
async def get_holding_distribution(token):
    """
    Get the holding distribution of a token.
    """
    if token is None:
        print("Token not provided.")
        return None
    
    token_overview = await get_token_overview(token) 
 
    if token_overview:
        token_data = token_overview.get('data', {})
        holder_count = token_data.get('holder', 0)
        total_supply = token_data.get('mc', 0)
        symbol = token_data.get('symbol', '')
        name = token_data.get('name', '')
        logo_url = token_data.get('logoURI', '')
        liquidity = token_data.get('liquidity', 0)
        market_cap = token_data.get('mc', 0)
    else:
        print("Failed to fetch token overview.")
    token_info = {
        'symbol': symbol,
        'name': name,
        'logo_url': logo_url,
        'liquidity': liquidity,
        'market_cap': market_cap,
    }


    
    top_holders = await get_top_holders(token, TOP_HOLDERS_TO_CONSIDER)  # Fetch top holders *****************************************************************
    if not top_holders:
        print("Failed to fetch top holders.")
        return None
    
    ranges = await process_all_holders(top_holders, total_supply, token)
    
    # Convert ranges to percentage
    actually_retrieved_holders = sum(ranges.values())
    results = [{k: (round((v / actually_retrieved_holders * 100),2)) for k, v in ranges.items()}, {"holder_count": holder_count, 'retrieved_holders': actually_retrieved_holders, "Symbol": symbol, "Name": name}, token_info]  
    
    return results

# Main execution function
if __name__ == "__main__":
    start_time = time.time()
    token = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"  # Example token
    result = asyncio.run(get_holding_distribution(token))
    print(result)
    print(f"Execution time: {time.time() - start_time} seconds")
