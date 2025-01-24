import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .utils.wallet_utils import get_wallet_age, get_wallet_age_readable
from .utils.token_utils import get_top_holders, get_token_overview
executor = ThreadPoolExecutor(max_workers=50)

async def run_blocking_fn(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


async def fresh_wallets(token: str, limit: int):
    """
    Fetch info regarding top holders of a token, including the age of each wallet.
    """
    top_holders_task = asyncio.create_task(get_top_holders(token, limit))
    token_overview_task = asyncio.create_task(get_token_overview(token))
    holders, token_overview = await asyncio.gather(top_holders_task, token_overview_task)


    tasks = [
        asyncio.create_task(fetch_wallet_info(index + 1, holder['owner']))
        for index, holder in enumerate(holders)
    ]
    wallet_results = await asyncio.gather(*tasks)


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
        token_info = None

    return {"token_info": token_info, "items": wallet_results}


async def fetch_wallet_info(count: int, wallet: str):
    """
    Fetches wallet age and returns the data.
    """
    age = await get_wallet_age(wallet)
    age_readable = await run_blocking_fn(get_wallet_age_readable, wallet, age)

    return {
        'count': count,
        'wallet': wallet,
        'age': age,
        'age_readable': age_readable,
    }


if __name__ == "__main__":
    start_time = time.time()
    token = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"
    limit = 50
    result = asyncio.run(fresh_wallets(token, limit))
    with open("backend/commands/outputs/fresh_wallets.json", "w") as f:
        f.write(json.dumps(result, indent=4))
    print(json.dumps(result, indent=4))
    print("Execution time:", time.time() - start_time)
