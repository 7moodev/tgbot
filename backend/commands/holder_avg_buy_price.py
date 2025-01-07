import httpx
import os
import asyncio
from backend.commands.utils.token_utils import get_rpc, get_top_holders, get_token_overview
from backend.commands.utils.wallet_utils import get_wallet_avg_price
import time

async def get_holder_avg_buy_price(token: str, limit: int):
    """
    Get the average buy price of a token for its top holders
    """
    token_overview = await get_token_overview(token)
    if token_overview:
        token_data = token_overview.get('data', {})
        symbol = token_data.get('symbol', '')
        name = token_data.get('name', '')
        logo_url = token_data.get('logo_uri', '')
        liquidity = token_data.get('liquidity', 0)
        market_cap = token_data.get('mc', 0)
    else:
        symbol = name = logo_url = ''
        liquidity = market_cap = 0
    token_info = {
        'symbol': symbol,
        'name': name,
        'logo_url': logo_url,
        'liquidity': liquidity,
        'market_cap': market_cap,
    }
    results = [token_info]
    holders = await get_top_holders(token, limit)
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_holder_avg_price(holder['owner'], token, client)
            for holder in holders
        ]
        responses = await asyncio.gather(*tasks)
        avg_buy_price_sum = 0
        for holder, avg_buy_price in zip(holders, responses):
            holder_result = {
                'address': holder['owner'],
                'avg_buy_price': avg_buy_price
            }
            results.append(holder_result)
            if avg_buy_price is not None:
                avg_buy_price_sum += avg_buy_price
        avg_buy_price = avg_buy_price_sum / len(holders) if holders else 0
        results.append({
            'avg_buy_price': avg_buy_price
        })
        return results
async def fetch_holder_avg_price(holder: str, token: str, client: httpx.AsyncClient):
    print("Fetching avg buy price for", holder, "in", token)
    """
    Fetch the average buy price of a token for a specific wallet
    """
    return await get_wallet_avg_price(holder, token, "buy", client)
if __name__ == "__main__":
    token_id = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"
    limit = 20
    start_time = time.time()
    results = asyncio.run(get_holder_avg_buy_price(token_id, limit))
    print(results)
    print(f"Execution time: {time.time() - start_time} seconds")