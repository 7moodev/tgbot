"""
token_info from tokens database

minimum 24h volume
minimum # holders
minimum market cap

"""

import asyncio
from dataclasses import dataclass
import json
import time
from typing import Any

import httpx
from backend.bot.parser import check_noteworthy
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.api_entity import ApiRequestParams
from backend.commands.utils.api.entities.token_entities import TrendingTokenEntity, TrendingTokenForX
from backend.commands.utils.services.log_service import LogService
from .x_openrouter_api import generate_x_message

logger = LogService("XBOT")
console = logger

THRESHOLDS = {
    "volume24hUSD": 10_000_000,
    "marketcap": 1_000_000,
    "holder": 2_000,
    "created": int((time.time() - 24 * 60 * 60)),
}
TRENDING_TOKENS_AMOUNT = 1
TOP_HOLDER_AMOUNT = 50

"""
X number of whales just aped $BONK. The current MC is $XYZ
"""


async def get_trending_tokens(limit = TRENDING_TOKENS_AMOUNT) -> list[TrendingTokenEntity]:
    filtered_trending_tokens: list[TrendingTokenForX] = []
    offset = 0
    fetch_limit = 20
    while len(filtered_trending_tokens) < limit:
        trending_tokens_response = await birdeyeApiService.get_trending_list(ApiRequestParams(limit=fetch_limit, offset=offset))
        if not trending_tokens_response["success"]:
            return

        trending_tokens: list[TrendingTokenEntity] = trending_tokens_response["data"]["tokens"]
        filtered_by_volume_and_mc: list[TrendingTokenEntity] = list(
            filter(
                lambda t: (
                    t['volume24hUSD'] > THRESHOLDS['volume24hUSD'] and
                    t['marketcap'] > THRESHOLDS['marketcap']
                ),
                trending_tokens
            )
        )
        # filtered_by_volume_and_mc = trending_tokens
        filtered_by_time = await get_filtered_by_time(filtered_by_volume_and_mc)
        filtered_by_holders = await get_filtered_by_holders(filtered_by_time)
        # trending_tokens.append(TrendingTokenForX(mc=t["marketcap"], symbol=t["symbol"] ) for t in filtered_by_holders)

        filtered_trending_tokens.extend([
            TrendingTokenForX(address=t['address'], symbol=t["symbol"], marketcap=t["marketcap"])
            for t in filtered_by_holders
        ])

        offset += fetch_limit

    return filtered_trending_tokens

async def get_filtered_by_time(tokens: list[TrendingTokenEntity]) -> list[TrendingTokenEntity]:
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_creation_info(token):
            token_creation_info = await birdeyeApiService.get_token_creation_info(
                token["address"],
                token["symbol"]
            )
            if (
                token_creation_info["success"]
                # and token_creation_info["data"]["blockUnixTime"] > THRESHOLDS["created"]
            ):
                return token
            return None

        creation_info_tasks = [
            get_creation_info(token) for token in tokens
        ]
        filtered_by_time = [
            token for token in await asyncio.gather(*creation_info_tasks) if token
        ]

    return filtered_by_time

async def get_filtered_by_holders(tokens: list[TrendingTokenEntity]) -> list[TrendingTokenEntity]:
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_token_overview(token):
            token_overview = await birdeyeApiService.get_token_overview(
                token["address"],
                token["symbol"]
            )
            if token_overview == None:
                return None
            if (
                token_overview["success"]
                and token_overview["data"]["holder"] > THRESHOLDS["holder"]
            ):
                return token
            return None

        overview_tasks = [get_token_overview(token) for token in tokens]
        filtered_by_holders = [
            token for token in await asyncio.gather(*overview_tasks) if token
        ]

    return filtered_by_holders

def get_amount_of_whales(top_holder_holdings: list[Any]) -> int:
    amount_of_whales = 0
    top_holders= top_holder_holdings['items']
    noteworthy = check_noteworthy(top_holders)
    for holder in noteworthy:
        dollar_token_share = holder['net_worth']- holder['net_worth_excluding']
        if dollar_token_share > 100_000:
            amount_of_whales += 1
    return amount_of_whales

async def init(address: str = None):
    # 1. Get trending tokens
    if address:
        trending_tokens
        pass
    else:
        trending_tokens = await get_trending_tokens()
    if trending_tokens == None:
        return

    # 2. Call /top on tokens from (1.)
    amount_of_whales_list = []
    for token in trending_tokens:
        # top_holders_response = await get_top_holders_holdings(token=token["address"], limit=TOP_HOLDER_AMOUNT)
        top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=0) # =0 for debugging, returns json
        if top_holders_holdings == None:
            continue
        amount_of_whales = get_amount_of_whales(top_holders_holdings)
        amount_of_whales_list.append(amount_of_whales)
    tokens_for_x: list[TrendingTokenForX] = [
        {
            "address": token["address"],
            "symbol": token["symbol"],
            "marketcap": token["marketcap"],
            "num_of_holders": amount_of_whales_list[i]
        }
        for i, token in enumerate(trending_tokens)
    ]

    # 3. Mix in AI formulation
    symbols = [t["symbol"] for t in tokens_for_x]
    ai_response = await generate_x_message(symbols, local = True)
    response_content = ai_response["choices"][0]['message']['content']
    response_content_processed = response_content.replace("```json\n", "").replace("\n```", "")
    as_json = json.loads(response_content_processed)
    closing = as_json["closings"]


    # 4. Post to X
    """
    X number of whales just aped $BONK. The current MC is $XYZ
    """
    for i, token in enumerate(tokens_for_x):
        message = f"{token['num_of_holders']} whales just aped ${token['symbol']}. The current MC is ${token['marketcap']}, {closing[i]}."
        message += message + f"\n\n Munki"
        console.log(message)

    return tokens_for_x


if __name__ == "__main__":
    asyncio.run(init())

# python -m backend.xBot.x_bot
