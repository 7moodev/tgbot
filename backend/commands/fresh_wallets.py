import json
import requests
import time
from .utils.wallet_utils import get_wallet_age, get_wallet_age_readable
from .utils.token_utils import get_top_holders, get_token_overview
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Set up the ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)

# Helper function to run blocking functions in threads
async def run_blocking_fn(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


async def fresh_wallets(token: str, limit: int):
    count = 0
    """
    Fetch info regarding top holders of a token, in regards to the age of each wallet.
    """
    holders = await get_top_holders(token, limit)
    res = []

    # Creating a list of tasks for fetching wallet data concurrently
    tasks = []
    for holder in holders:
        count += 1
        wallet = holder['owner']
        tasks.append(
             fetch_wallet_info(count,wallet)
        )
    # Await all tasks and collect results
    res = await asyncio.gather(*tasks)
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
    return token_info, res

async def fetch_wallet_info(count,wallet: str):
    """
    Fetches wallet age and returns the data.
    This function will run in a separate thread for each wallet to avoid blocking.
    """

    age = await run_blocking_fn(get_wallet_age, wallet)
    age_readable = (get_wallet_age_readable(wallet,age))
    
    return {
        'count': count,
        'wallet': wallet,
        'age': age,
        'age_readable': age_readable
    }

if __name__ == "__main__":
    start_time = time.time()
    token = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"
    limit = 100
    print(asyncio.run(fresh_wallets(token, limit)))
    print("Execution time:", time.time() - start_time)
