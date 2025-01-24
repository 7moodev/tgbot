import requests
from backend.commands.utils.general_utils import get_rpc

import time
import asyncio
import httpx


def get_wallet_age(wallet:str=None,  max_signatures:int=5000, bot_filter:bool=True):
    print("Getting wallet age for", wallet)
    """
    Get the blocktime of the oldest transaction of a wallet in unix time. 
    Returns 0 for exchanges
    Costs 0 credits
    """	
    headers = {
        "Content-Type": "application/json",
    }
    if wallet is None:
        return None
    all_signatures = []
    before = None
    time_nowin_unix = int(time.time())
    count = 0
    while True:
        if all_signatures:
            bot_check = bot_filter and time_nowin_unix - all_signatures[-1].get('blockTime') < 72000
        else:
            bot_check = False
        if len(all_signatures) > max_signatures or bot_check:
            return 0
        params = [wallet, {"limit": 1000}]
        if before:
            params[1]["before"] = before
        data = {
            "jsonrpc": "2.0",
            "method": "getSignaturesForAddress", 
            "params": params,
            "id": 1
        }
        response = requests.post(get_rpc(), headers=headers, json=data)
        if response.status_code != 200:
            print("Error fetching signatures for", wallet)
            return None
        result = response.json().get('result', [])
        if not result:
            break
        all_signatures.extend(result)
        if len(result) < 1000:
            break
        before = result[-1]['signature']
    # Return the blocktime of the last signature (oldest transaction)
    if all_signatures:
        return all_signatures[-1].get('blockTime')
    return None


async def get_wallet_age1(wallet: str = None, max_signatures: int = 5000, bot_filter: bool = True):
    """
    Get the blocktime of the oldest transaction of a wallet in unix time.
    Returns 0 for exchanges or bot activity.
    """
    if wallet is None:
        return None

    headers = {"Content-Type": "application/json"}
    all_signatures_count = 0
    oldest_block_time = None
    before = None
    time_now_unix = int(time.time())

    async with httpx.AsyncClient() as client:
        while True:
            # Exit if max_signatures is exceeded
            if all_signatures_count > max_signatures:
                return oldest_block_time

            # Prepare request payload
            params = [wallet, {"limit": 1000}]
            if before:
                params[1]["before"] = before
            data = {"jsonrpc": "2.0", "method": "getSignaturesForAddress", "params": params, "id": 1}

            try:
                # Make asynchronous request
                response = await client.post(get_rpc(), headers=headers, json=data)
                response.raise_for_status()
                result = response.json().get('result', [])

                if not result:  # No more signatures
                    break

                # Update the count and check for bot activity
                all_signatures_count += len(result)
                if bot_filter and time_now_unix - result[-1].get('blockTime', 0) < 72000:
                    return 0

                # Update oldest block time and before signature
                oldest_block_time = result[-1].get('blockTime', oldest_block_time)
                before = result[-1]['signature']

                # Exit early if fewer than 1000 results are returned
                if len(result) < 1000:
                    break

            except (httpx.RequestError, KeyError) as e:
                print(f"Error fetching wallet age for {wallet}: {str(e)}")
                return None

    return oldest_block_time

timeNow = int(time.time())
print(asyncio.run(get_wallet_age1("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF")))
print("Execution time:", time.time() - timeNow)