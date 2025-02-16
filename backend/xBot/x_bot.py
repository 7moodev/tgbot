"""
token_info from tokens database

minimum 24h volume
minimum # holders
minimum market cap

"""

import asyncio
import json
import time
from typing import List

import httpx
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.api_entity import ApiRequestParams
from backend.commands.utils.api.entities.token_entities import TrendingTokenEntity
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


async def get_trending_tokens(limit = TRENDING_TOKENS_AMOUNT) -> list[TrendingTokenEntity]:
    trending_tokens = []
    offset = 0
    fetch_limit = 20
    while len(trending_tokens) < limit:
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

        filtered_by_time = await get_filtered_by_time(filtered_by_volume_and_mc, limit)
        filtered_by_holders = await get_filtered_by_holders(filtered_by_time)

        trending_tokens.extend(filtered_by_holders)
        offset += fetch_limit

    return trending_tokens

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
                and token_creation_info["data"]["blockUnixTime"] > THRESHOLDS["created"]
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

async def init(address: str = None):
    if address:
        potential_tokens
        pass
    else:
        potential_tokens = await get_trending_tokens()
    if potential_tokens == None:
        return

    # log and format json with 4 spaces

    # 2. Call /top on tokens from (1.)
    top_holders = []
    for token in potential_tokens:
        # continue
        top_holders_response = await birdeyeApiService.get_top_holders(token["address"], symbol=token["symbol"], limit=3)
        if top_holders_response == None:
            continue
        top_holders.append(top_holders_response)

    # 3. Mix in Eliza
    console.log('>>>> _ >>>> ~ file: x_bot.py:118 ~ top_holders:', top_holders)  # fmt: skip
    # ai_response = generate_x_message

    # 4. Post to X


if __name__ == "__main__":
    asyncio.run(init())

# python -m backend.xBot.x_bot
