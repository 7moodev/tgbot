import os
import asyncio
import json
import time
from typing import List, Dict, Any

from .utils.token_utils import get_token_creation_info, get_token_overview, get_top_holders
from .utils.general_utils import get_top_traders
from .utils.wallet_utils import get_wallet_portfolio


whales_file_path = "backend/commands/constants/whales.json"
with open(whales_file_path, 'r') as f:
    whales = json.load(f)
    whales = set(whales['items'])

SEMAPHORE_LIMIT = 15  


async def rate_limited_call(func, *args, **kwargs):
    """Wraps a function call with rate limiting."""
    async with asyncio.Semaphore(SEMAPHORE_LIMIT):
        await asyncio.sleep(1 / SEMAPHORE_LIMIT)
        return await func(*args, **kwargs)


async def get_wallet_portfolio_refined(wallet: str, token: str):
    """Fetch and refine wallet portfolio."""
    portfolio = await rate_limited_call(get_wallet_portfolio, wallet)

    if "error" in portfolio:
        return {
            'wallet': wallet,
            'error': portfolio.get('error', 'Unknown error')
        }

    net_worth = portfolio.get('totalUsd', 0)
    holdings = portfolio.get('items', [])
    top_holdings = [holdings[i] if i < len(holdings) else 0 for i in range(3)]

    return {
        'wallet': wallet,
        'net_worth': net_worth,
        'net_worth_excluding': extract_holding_excluding(portfolio, token),
        'first_top_holding': top_holdings[0],
        'second_top_holding': top_holdings[1],
        'third_top_holding': top_holdings[2],
    }


def extract_holding_excluding(portfolio: Dict[str, Any], token: str) -> float:
    """Calculate net worth excluding a specific token."""
    for holding in portfolio.get('items', []):
        if holding['address'] == token:
            return portfolio['totalUsd'] - holding['valueUsd']
    return portfolio['totalUsd']


async def fetch_token_data(token: str, limit: int):
    """Fetch token-related data in parallel."""
    return await asyncio.gather(
        get_token_creation_info(token),
        get_token_overview(token),
        get_top_traders(0),
        get_top_holders(token, limit),
    )


async def process_holder(holder, index, token_info, token, top_traders):
    """Process individual holder data."""
    wallet_portfolio = await get_wallet_portfolio_refined(holder['owner'], token)
    if 'error' in wallet_portfolio:
        return None

    wallet_portfolio['amount'] = holder['ui_amount']
    wallet_portfolio['share_in_percent'] = (
        float(holder['ui_amount']) / float(token_info['supply']) * 100
    )

    if wallet_portfolio['net_worth_excluding'] > 50000:
        entry = {'holderIdx': index+1, "type": 0, "address": holder, 'portfolio': wallet_portfolio}
        for trader in top_traders:
            if trader['address'] == holder['owner']:
                entry['stats'] = {
                    'pnl': trader['pnl'],
                    'volume': trader['volume'],
                    'trade_count': trader['trade_count'],
                }
                entry['type'] = 1
        return entry
    return None


async def get_noteworthy_addresses(token: str, limit: int = 50):
    """Fetch and process noteworthy addresses."""
    token_creation_info, token_overview, top_traders, top_holders = await fetch_token_data(token, limit)

    token_info = {
        'symbol': token_overview['data']['symbol'],
        'name': token_overview['data']['name'],
        'logoURI': token_overview['data']['logoURI'],
        'liquidity': token_overview['data']['liquidity'],
        'market_cap': token_overview['data']['mc'],
        'supply': token_overview['data']['supply'],
        'circulatingSupply': token_overview['data']['circulatingSupply'],
        'realMc': token_overview['data']['realMc'],
        'holder': token_overview['data']['holder'],
        'creationTime': token_creation_info['blockUnixTime'],
    }
    tasks = [
        process_holder(holder, index, token_info, token, top_traders)
        for index, holder in enumerate(top_holders)
    ]
    results = await asyncio.gather(*tasks)

    return {
        'token_info': token_info,
        'valid_results': len([r for r in results if r]),
        'items': [r for r in results if r],
    }


if __name__ == "__main__":
    timenow = time.time()
    result = asyncio.run(get_noteworthy_addresses("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump", 5))
    with open("backend/commands/outputs/noteworthy_addresses.json", "w") as f:
        f.write(json.dumps(result, indent=4))
    print(json.dumps(result, indent=4))
    print(f"Execution Time: {time.time() - timenow:.2f} seconds")
