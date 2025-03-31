import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
from .utils.wallet_utils import  get_wallet_age_readable, get_wallet_age
from .utils.token_utils import get_top_holders, get_token_overview, get_token_creation_info, get_token_supply, get_rpc
from .utils.general_utils import get_tx
import httpx
import os

FRESH_DEFINITION_IN_DAYS = 14
MAX_WORKERS = min(100, os.cpu_count() * 3)  # Adjust based on the number of CPU cores and workload

async def fetch_wallet_details_async(holder, total_supply, idx: int):
    """Fetch details for a single wallet asynchronously."""
    current_time = time.time()
    try:
        raw_tx = await get_wallet_age(holder['owner'], time_out=1, max_age=FRESH_DEFINITION_IN_DAYS * 24 * 60 * 60)
        age = raw_tx.get('blockTime')

    except Exception:
        age = None  # Handle exceptions gracefully
    if age is None:
        age = current_time
    if current_time - age < 60 * 60 * 24 * FRESH_DEFINITION_IN_DAYS:
        if current_time - age < 60 * 60 * 24:  # Filter out bots and LPs
            return None
        tx = await get_tx(raw_tx['signature'])
        funding_rouce = await get_funding_source(tx)
        holding = int(holder['ui_amount'])
        holding_pct = round(holding / total_supply * 100, 3)
        age_readable = await get_wallet_age_readable(holder['owner'], age)
        return {
            'count': idx,  # Assigning the index as the count
            'address': holder['owner'],
            'holding': holding,
            'holding_pct': holding_pct,
            'age': age,
            'age_readable': age_readable,
            'funding_source': funding_rouce
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
    if limit == 0:
        with open('backend/commands/outputs/fresh_wallets_v2.json', 'r') as f:
            return json.load(f)

    total_supply = await get_token_supply(token)
    top_holders = (await get_top_holders(token, limit))
    token_overview = await get_token_overview(token)
    token_creation_info = await get_token_creation_info(token)

    # Process token overview
    if token_overview:
        token_overview = token_overview['data']
        token_info = {
            'price': token_overview['price'],
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview.get('logoURI', None),
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['marketCap'],
            'supply': total_supply,
            'circulatingSupply': token_overview['circulatingSupply'],
            'fdv': token_overview['fdv'],
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
    with open('backend/commands/outputs/fresh_wallets_v2.json', 'w') as f:
        json.dump({"token_info": token_info, 'valid_results': len(items), "items": items}, f, indent=4)
    return {"token_info": token_info, 'valid_results': len(items), "items": items}

# async def get_wallet_age(wallet: str = None, time_out: int = None) -> int:
#     """
#     Get the blocktime of the oldest transaction of a wallet in unix time.
#     Returns 0 for exchanges or bot activity.
#     """
#     print("Getting wallet age for", wallet)
#     if wallet is None:
#         return None

#     headers = {"Content-Type": "application/json"}
#     all_signatures_count = 0
#     oldest_block_time = None

#     async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
#         params = [wallet, {"limit": 1000}]
#         data = {"jsonrpc": "2.0", "method": "getSignaturesForAddress", "params": params, "id": 1}
#         try:
#             if time_out is not None:
#                 response = await client.post(await get_rpc(), headers=headers, json=data, timeout=time_out)
#             else:
#                 response = await client.post(await get_rpc(), headers=headers, json=data)
#             response.raise_for_status()
#             result = response.json().get('result', [])
#             if not result: 
#                 return None
#             return  result[-1]

#         except (httpx.RequestError, KeyError, httpx.HTTPStatusError) as e:
#             print(response.json())
#             print(str(e))
#             print(f"Error fetching wallet age for {wallet}: {str(e)}")
#             return None
#     print("Returning wallet age for", wallet)
#     return oldest_block_time
async def get_funding_source(transaction):

    try:
        if transaction:
            instructions = transaction["result"]["transaction"]["message"]["instructions"]
            for instruction in instructions:
                if "parsed" in instruction:
                    type = instruction["parsed"]["type"]
                    if type == 'transfer' or type == 'transferChecked':
                        return instruction['parsed']['info']['source']
        else:
            return None
    except Exception as e:
        print(e)
        print("Failed to analyse tx and find source")
        return None
if __name__ == "__main__":
    start_time = time.time()
    token = "6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump"
    # addy = "3fZTvPuYYFVFgY3vQzqQaYWydhavcR1mbs9cerFKEAKY"
    # # addy1 = "5BmsaY2SBiuRQsDpRRiqCvKnhDA5UX89VsHxDL5muAhu"
    # sig = (asyncio.run(get_wallet_age(addy)))
    # #print(sig)
    # data = asyncio.run(get_tx(sig['signature']))
    # #print(json.dumps(data, indent=2))
    # print(asyncio.run(get_funding_source(data)))
    # instructions = data["result"]["transaction"]["message"]["instructions"]
    # print(json.dumps(instructions, indent=2))
    # #print(instructions)
    #print(asyncio.run(get_wallet_age("Fnz5CaHjX8SBuJAL6cKwLVY6QnAT7o5HNxz47qbYzMMW")))
    async def main():
        result = await fresh_wallets_v2(token, 100)
        print(json.dumps(result, indent=2))
    asyncio.run(main())
    print(f"Execution time: {time.time() - start_time} seconds")
    
