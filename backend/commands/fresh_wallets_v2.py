import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
from .utils.wallet_utils import get_wallet_age, get_wallet_age_readable
from .utils.token_utils import get_top_holders, get_token_overview, get_token_creation_info, get_token_supply
import os

FRESH_DEFINITION_IN_DAYS = 7
MAX_WORKERS = min(100, os.cpu_count() * 3)  # Adjust based on the number of CPU cores and workload

async def fetch_wallet_details_async(holder, total_supply, idx: int):
    """Fetch details for a single wallet asynchronously."""
    current_time = time.time()
    try:
        age = await get_wallet_age(holder['owner'], 999, time_out=1)
    except Exception:
        age = None  # Handle exceptions gracefully
    if age is None:
        age = current_time
    if current_time - age < 60 * 60 * 24 * FRESH_DEFINITION_IN_DAYS:
        if current_time - age < 60 * 60 * 24:  # Filter out bots and LPs
            return None
        holding = int(holder['ui_amount'])
        holding_pct = round(holding / total_supply * 100, 2)
        age_readable = await get_wallet_age_readable(holder['owner'], age)
        return {
            'count': idx,  # Assigning the index as the count
            'address': holder['owner'],
            'holding': holding,
            'holding_pct': holding_pct,
            'age': age,
            'age_readable': age_readable
        }
    return None

def fetch_wallet_details_sync(holder, total_supply, idx: int):
    """Fetch wallet details in a synchronous blocking way."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(fetch_wallet_details_async(holder, total_supply, idx))
    finally:
        loop.close()

def fetch_wallets_in_parallel(holders, total_supply):
    """Fetch wallet details using parallel processing."""
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(
            fetch_wallet_details_sync,
            holders,
            [total_supply] * len(holders),
            range(len(holders))  # Pass index for each holder
        ))
    return [result for result in results if result is not None]

async def fresh_wallets_v2(token: str, limit: int):
    """Fetch and process fresh wallets for a token."""
    total_supply = await get_token_supply(token)
    top_holders = await get_top_holders(token, limit)
    token_overview = await get_token_overview(token)
    token_creation_info = await get_token_creation_info(token)

    # Process token overview
    if token_overview:
        token_overview = token_overview['data']
        token_info = {
            'price': token_overview['price'],
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview['logoURI'],
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['mc'],
            'supply': total_supply,
            'circulatingSupply': token_overview['circulatingSupply'],
            'realMc': token_overview['realMc'],
            'holder': token_overview['holder'],
            'extensions': token_overview['extensions'],
            'priceChange1hPercent': token_overview['priceChange1hPercent'],
        }
        if token_creation_info:
            token_info['creationTime'] = token_creation_info['blockUnixTime']
    else:
        token_info = {}

    # Fetch wallet details in parallel
    items = await asyncio.to_thread(fetch_wallets_in_parallel, top_holders, total_supply)

    return {"token_info": token_info, 'valid_results': len(items), "items": items}

if __name__ == "__main__":
    start_time = time.time()
    token = "6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump"

    async def main():
        result = await fresh_wallets_v2(token, 100)
        print(json.dumps(result, indent=2))

    asyncio.run(main())
    print(f"Execution time: {time.time() - start_time} seconds")
