"""
token_info from tokens database

minimum 24h volume
minimum # holders
minimum market cap

"""

import asyncio
import time
from typing import List

import httpx
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.token_entities import TrendingTokenEntity
from backend.commands.utils.services.log_service import LogService

logger = LogService("XBOT")
console = logger

THRESHOLDS = {
    "volume24hUSD": 10_000_000,
    "marketcap": 1_000_000,
    "holder": 2_000,
    "created": int((time.time() - 24 * 60 * 60)),
}


async def get_potential_tokens():
    # 1. Call GET /trending from birdeye
    trending_tokens_response = await birdeyeApiService.get_trending_list()
    if not trending_tokens_response["success"]:
        return

    trending_tokens = trending_tokens_response["data"]["tokens"]
    # 1.1 Filter
    # minimum 24h volume > $10M
    # minimum market cap > $1M
    # via /trending_list
    # filtered_by_volume_and_mc = list(filter(lambda x: x['volume24hUSD'] > THRESHOLDS['volume24hUSD'] and x['marketcap'] > THRESHOLDS['marketcap'], trending_tokens))
    filtered_by_volume_and_mc = trending_tokens
    # only log the token names
    console.log( ">>>> _ >>>> ~ filtered_by_volume:", [x["name"] for x in filtered_by_volume_and_mc],)  # fmt: skip

    # newly created within 24h
    # token_creation_info
    filtered_by_time = []
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_creation_info(token):
            # console.log(">>>> _ >>>> ~ file: x_bot.py:51 ~ token:", token)
            token_creation_info = await birdeyeApiService.get_token_creation_info(
                token["address"]
            )
            if (
                token_creation_info["success"]
                and token_creation_info["data"]["blockUnixTime"] > THRESHOLDS["created"]
            ):
                return token
            return None

        creation_info_tasks = [
            get_creation_info(token) for token in filtered_by_volume_and_mc
        ]
        filtered_by_time = [
            token for token in await asyncio.gather(*creation_info_tasks) if token
        ]

    # minimum # holder > 2000
    # via token_overview
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_token_overview(token):
            token_overview = await birdeyeApiService.get_token_overview(
                token["address"]
            )
            if token_overview == None:
                return None
            if (
                token_overview["success"]
                and token_overview["data"]["holder"] > THRESHOLDS["holder"]
            ):
                return token
            return None

        overview_tasks = [get_token_overview(token) for token in filtered_by_time]
        filtered_by_holders = [
            token for token in await asyncio.gather(*overview_tasks) if token
        ]

        final_tokens: List[TrendingTokenEntity] = filtered_by_holders

    return final_tokens


async def init(address: str = None):
    if address:
        potential_tokens
        pass
    else:
        potential_tokens = await get_potential_tokens()
    if potential_tokens == None:
        return

    # 2. Call /top on tokens from (1.)
    top_holders = []
    for token in potential_tokens:
        top_holders_response = await birdeyeApiService.get_top_holders(token["address"])
        if not top_holders_response["success"]:
            continue
        top_holders.append(top_holders_response["data"])

    # 3. Mix in Eliza
    console.log(">>>> _ >>>> ~ top_holders:", top_holders)

    # 4. Post to X


if __name__ == "__main__":
    asyncio.run(init())

# python -m backend.xBot.x_bot
