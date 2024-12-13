import os
import requests
import time
import base58
import functools
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession, ClientError
import math
import aiohttp
from token_helper import getTokenOverview, getTopHolders


birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
solscanapi = os.environ.get('solscan')

async def fetchWalletPortfolio(session, wallet: str):
    """
    Asynchronously fetch the wallet portfolio with rate limiting.
    """
    url = f"https://public-api.birdeye.so/v1/wallet/token_list?wallet={wallet}"
    headers = {
        "accept": "application/json",
        "chain": "solana",
        "X-API-KEY": birdeyeapi
    }

    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        data = await response.json()
        if not data.get('success', True):
            return {"error": f"Failed to fetch portfolio for wallet {wallet}"}
        return data
async def getWalletPortfolio(count, holder, session, total_supply, token):
    """
    Process a single holder with adaptive pacing.
    """
    wallet = holder['owner']
    amount = holder['ui_amount']
    share_in_percent = float(amount) / total_supply * 100
    portfolio = await fetchWalletPortfolio(session, wallet)
    if "error" in portfolio:
        return {f'wallet {count}': portfolio}

    net_worth = round(portfolio['data']['totalUsd'], 0)
    # Extract holdings
    holdings = portfolio['data']['items']
    for item in holdings:
        if item['address'] == token:
            net_worth_excluding = net_worth - item['valueUsd']
            break  
        else:
            net_worth_excluding = net_worth

    # Get top holdings efficiently
    top_holdings = holdings[:3]
    return {
        f'wallet {count}': {
            'wallet': wallet,
            'amount': amount,
            'shareInPercent': round(share_in_percent, 3),
            'netWorth': net_worth,
            'netWorthExcluding': net_worth_excluding,
            'firstTopHolding': top_holdings[0] if len(top_holdings) > 0 else None,
            'secondTopHolding': top_holdings[1] if len(top_holdings) > 1 else None,
            'thirdTopHolding': top_holdings[2] if len(top_holdings) > 2 else None,
        }
    }

async def getHoldingDistribution(token: str = None):
    """
    Get the holding distribution of a token.
    """
    if token is None:
        print("Token not provided.")
        return None

    considerOnlyPercent = 0.1

    # Fetch token overview
    tokenOverview = getTokenOverview(token)  # Assuming this is a synchronous function
    if not tokenOverview or not tokenOverview.get('data'):
        print("Failed to fetch token overview.")
        return None

    holder_count = tokenOverview['data'].get('holder', 0)
    total_supply = tokenOverview['data'].get('mc', 0)
    print(f"Getting holding distribution for {token} with {holder_count} holders")

    # Fetch top holders
    topHolders = await getTopHolders(token, round(holder_count * considerOnlyPercent))
    if not topHolders:
        print("Failed to fetch top holders.")
        return None

    ranges = {
        "0-20": 0,
        "20-250": 0,
        "250-2000": 0,
        "2000-10000": 0,
        "10000+": 0,
    }

    semaphore = asyncio.Semaphore(15)  # Limit to 10 concurrent tasks

    async def process_holder(session, count, holder):
        print(f"Processing holder {holder['owner']}")
        async with semaphore:  # Ensure no more than 10 concurrent tasks
            try:
                portfolio = await getWalletPortfolio(count, holder, session, total_supply, token)
                if "error" in portfolio:
                    print(f"Error in portfolio for wallet {holder['owner']}: {portfolio}")
                    return

                wallet_data = portfolio.get(f'wallet {count}')
                if not wallet_data:
                    print(f"No data returned for wallet {holder['owner']}")
                    return

                net_worth_excluding = wallet_data.get("netWorthExcluding")
                if net_worth_excluding is None:
                    print(f"Missing key 'valueUsd' for holder {holder['owner']}. Skipping...")
                    return

                # Categorize net worth
                if net_worth_excluding < 20:
                    ranges["0-20"] += 1
                elif net_worth_excluding < 250:
                    ranges["20-250"] += 1
                elif net_worth_excluding < 2000:
                    ranges["250-2000"] += 1
                elif net_worth_excluding < 10000:
                    ranges["2000-10000"] += 1
                else:
                    ranges["10000+"] += 1
            except Exception as e:
                print(f"Error processing holder {holder['owner']}: {e}")

    async def process_all_holders():
        # Use batched processing to avoid creating too many tasks simultaneously
        batch_size = 10
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(topHolders), batch_size):
                tasks = [
                    process_holder(session, idx + 1, holder)
                    for idx, holder in enumerate(topHolders[i:i + batch_size])
                ]
                await asyncio.gather(*tasks)
                # Throttle to avoid exceeding API rate limits
                await asyncio.sleep(1)

    await process_all_holders()
    return [{k: v} for k, v in ranges.items()]



if __name__ == "__main__":
    print(asyncio.run(getHoldingDistribution("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump")))