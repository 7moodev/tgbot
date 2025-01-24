import json
import time
import asyncio
import httpx
from typing import List, Dict, Any
from .utils.wallet_utils import get_wallet_age, get_wallet_age_readable
from .utils.token_utils import get_top_holders, get_token_overview

# Define API rate-limiting semaphore
API_RATE_LIMIT = 15
REQUEST_SEMAPHORE = asyncio.Semaphore(API_RATE_LIMIT)


async def fetch_wallet_info(count: int, wallet: str, session: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Asynchronously fetch wallet age and return the data.
    """
    async with REQUEST_SEMAPHORE:
        try:
            age = await get_wallet_age(wallet)
            age_readable = "pew"
        except Exception as e:
            return {
                "count": count,
                "wallet": wallet,
                "error": f"Failed to fetch wallet info: {str(e)}",
            }

        return {
            "count": count,
            "wallet": wallet,
            "age": age,
            "age_readable": age_readable,
        }


async def fetch_wallet_info_parallel(wallet_args: List[Dict[str, Any]], session: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """
    Execute `fetch_wallet_info` in parallel using asyncio.gather.
    """
    tasks = [
        fetch_wallet_info(count, wallet["owner"], session) for count, wallet in enumerate(wallet_args, start=1)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions in the results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append({"error": f"Exception occurred: {str(result)}"})
        else:
            processed_results.append(result)

    return processed_results


async def fresh_wallets(token: str, limit: int) -> Dict[str, Any]:
    """
    Fetch info regarding top holders of a token, including the age of each wallet using asyncio.
    """
    # Asynchronously fetch token holders and token overview
    holders = await get_top_holders(token, limit)
    token_overview = await get_token_overview(token)

    # Prepare token info
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

    # Use a single HTTP client session for all requests
    async with httpx.AsyncClient() as session:
        # Fetch wallet info concurrently
        wallet_results = await fetch_wallet_info_parallel(holders, session)

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
