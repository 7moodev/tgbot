import json
import time
import asyncio
import httpx
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any
from .utils.wallet_utils import get_wallet_age, get_wallet_age_readable
from .utils.token_utils import get_top_holders, get_token_overview, get_token_creation_info


async def fetch_wallet_info(count: int, wallet: str) -> Dict[str, Any]:
    """
    Fetch wallet age asynchronously.
    """
    try:
        age = await get_wallet_age(wallet)
        age_readable = await get_wallet_age_readable(wallet, age)
        return {
            "count": count,
            "wallet": wallet,
            "age": age,
            "age_readable": age_readable,
        }
    except Exception as e:
        return {
            "count": count,
            "wallet": wallet,
            "error": f"Failed to fetch wallet info: {str(e)}",
        }


def run_coroutine_in_process(args):
    """
    Run an async coroutine in a separate process.
    """
    count, wallet = args
    return asyncio.run(fetch_wallet_info(count, wallet))


async def fetch_wallet_info_multiprocessing(wallet_args: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process wallets using multiprocessing with ProcessPoolExecutor.
    """
    with ProcessPoolExecutor() as executor:
        # Create arguments as tuples for the executor
        args = [(count, wallet["owner"]) for count, wallet in enumerate(wallet_args, start=1)]

        # Submit tasks to the executor and collect futures
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, run_coroutine_in_process, arg) for arg in args]

        # Gather results
        results = await asyncio.gather(*tasks)
    return results


async def fresh_wallets(token: str, limit: int) -> Dict[str, Any]:
    """
    Fetch token holders and wallet information asynchronously, using multiprocessing for wallets.
    """
    try:
        # Fetch token holders and overview concurrently
        holders, token_overview = await asyncio.gather(
            get_top_holders(token, limit),
            get_token_overview(token)
        )
    except Exception as e:
        return {"error": f"Failed to fetch token data: {str(e)}"}

    token_creation_info = await get_token_creation_info(token)
    if token_overview :
        token_overview = token_overview['data']
        token_info = {
            'price': token_overview['price'],
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview['logoURI'],
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['mc'],
            'circulatingSupply': token_overview['circulatingSupply'],
            'realMc': token_overview['realMc'],
            'holder': token_overview['holder'],
            'extensions': token_overview['extensions'],
            'priceChange1hPercent': token_overview['priceChange1hPercent'],
        }
    else:
        token_info = {}

    # Fetch wallet information using multiprocessing
    wallet_results = await fetch_wallet_info_multiprocessing(holders)

    return {"token_info": token_info, "items": wallet_results}


if __name__ == "__main__":
    start_time = time.time()
    token = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"
    limit = 100
    result = asyncio.run(fresh_wallets(token, limit))
    with open("backend/commands/outputs/fresh_wallets.json", "w") as f:
        json.dump(result, f, indent=4)
    print(json.dumps(result, indent=4))
    print("Execution time:", time.time() - start_time)
