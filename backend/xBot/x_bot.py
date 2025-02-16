"""
token_info from tokens database

minimum 24h volume
minimum # holders
minimum market cap

"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import time
from typing import Any, Tuple

import httpx
from backend.bot.parser import check_noteworthy
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.api_entity import ApiRequestParams
from backend.commands.utils.api.entities.token_entities import TrendingTokenEntity, TrendingTokenForX
from backend.commands.utils.api.x_api_service import post_tweet
from backend.commands.utils.services.log_service import LogService
from backend.database.trending_token_entities_database import trendingTokenEntityDatabase
from .x_openrouter_api import generate_x_message

logger = LogService("XBOT")
console = logger

THRESHOLDS = {
    "volume24hUSD": 10_000_000,
    "marketcap": 1_000_000,
    "holder": 2_000,
    "created": int((time.time() - 24 * 60 * 60)),
}
TRENDING_TOKENS_AMOUNT = 5
FETCH_LIMIT = 20
OFFSET_LIMIT = 100
# OFFSET_LIMIT = FETCH_LIMIT
TOP_HOLDER_AMOUNT = 50
MINIMUM_DOLLAR_AMOUNT = 10

"""
X number of whales just aped $BONK. The current MC is $XYZ
"""


async def get_trending_tokens(limit = TRENDING_TOKENS_AMOUNT) -> list[TrendingTokenEntity]:
    filtered_trending_tokens: list[TrendingTokenForX] = []
    offset = 0
    while len(filtered_trending_tokens) < limit:
        if offset >= OFFSET_LIMIT:
            break
        trending_tokens_response = await birdeyeApiService.get_trending_list({"limit":FETCH_LIMIT, "offset":offset})
        if not trending_tokens_response["success"]:
            return

        trending_tokens: list[TrendingTokenEntity] = trending_tokens_response["data"]["tokens"]
        # trending_tokens: list[TrendingTokenEntity] = trendingTokenEntityDatabase.fetch_all()
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
        filtered_trending_tokens.extend([
            TrendingTokenForX(address=t['address'], symbol=t["symbol"], marketcap=t["marketcap"])
            for t in filtered_by_holders
        ])

        offset += FETCH_LIMIT
        console.log('>>>> _ >>>> ~ file: x_bot.py:80 ~ offset:', offset)  # fmt: skip
    console.log('>>>> _ >>>> ~ file: x_bot.py:46 ~ offset:', offset)  # fmt: skip

    timestamp = datetime.now().replace(microsecond=0)
    file_path = f"backend/commands/outputs/trending/1_trending_tokens_list_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(filtered_trending_tokens, f, indent=4)

    return filtered_trending_tokens

async def get_filtered_by_time(tokens: list[TrendingTokenEntity]) -> list[TrendingTokenEntity]:
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_creation_info(token):
            token_creation_info = await birdeyeApiService.get_token_creation_info(
                token["address"],
                token["symbol"],
                local=True
            )
            if (
                token_creation_info
                and token_creation_info["success"]
                and token_creation_info["data"]
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
                if token["symbol"] == "Unknown":
                    token["symbol"] = token_overview["data"]["symbol"]
                if token["name"] == "Unknown":
                    token["name"] = token_overview["data"]["name"]
                return token
            return None

        overview_tasks = [get_token_overview(token) for token in tokens]
        filtered_by_holders = [
            token for token in await asyncio.gather(*overview_tasks) if token
        ]

    return filtered_by_holders

def get_amount_of_holders(top_holder_holdings: list[Any]) -> Tuple[int, int]:
    amount_of_whales = 0
    amount_of_smart_wallets = 0
    top_holders= top_holder_holdings['items']
    noteworthy = check_noteworthy(top_holders)
    for holder in noteworthy:
        dollar_token_share = holder['net_worth']- holder['net_worth_excluding']
        if dollar_token_share > 100_000:
            amount_of_whales += 1
        elif dollar_token_share > MINIMUM_DOLLAR_AMOUNT:
            amount_of_smart_wallets += 1
    return amount_of_whales, amount_of_smart_wallets

def extract_json(input: str):
    index = input.find("\"symbols\"")
    while index != -1 and input[index] != "{":
        index = input[:index].rfind("{")

    end_index = input.rfind("}")
    if end_index != -1:
        input = input[:end_index + 1]
    if index != -1 and end_index != -1:
        json_str = input[index:end_index+1]
        try:
            as_json = json.loads(json_str)
            logger.log("as_json: ", as_json)
        except json.JSONDecodeError as e:
            logger.log("JSONDecodeError: ", e)
    else:
        logger.log("No JSON found")

    return as_json




async def init(address: str = None):
    # 1. Get trending tokens
    console.log("1. Get trending tokens ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    if address:
        trending_tokens
        pass
    else:
        trending_tokens = await get_trending_tokens()
    if trending_tokens == None:
        return

    # 2. Call /top on tokens from (1.)
    console.log("2. Call /top on tokens from (1.) ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    amount_of_holders_list = []
    for token in trending_tokens:
        top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=TOP_HOLDER_AMOUNT)
        # top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=0) # =0 for debugging, returns json
        if top_holders_holdings == None:
            continue
        holders = get_amount_of_holders(top_holders_holdings)
        amount_of_holders_list.append(holders)
    console.log('>>>> _ >>>> ~ file: x_bot.py:154 ~ amount_of_whales_list:', amount_of_holders_list)  # fmt: skip
    tokens_for_x: list[TrendingTokenForX] = [
        {
            "address": token["address"],
            "symbol": token["symbol"],
            "marketcap": token["marketcap"],
            "num_of_whales": amount_of_holders_list[i][0],
            "num_of_holders": amount_of_holders_list[i][1]
        }
        for i, token in enumerate(trending_tokens)
    ]
    timestamp = datetime.now().replace(microsecond=0)
    with open(f"backend/commands/outputs/trending/2_tokens_for_x_{timestamp}.json", "w") as f:
        json.dump(tokens_for_x, f, indent=4)

    # tokens_for_x=[{'address': '4MpXgiYj9nEvN1xZYZ4qgB6zq5r2JMRy54WaQu5fpump', 'symbol': 'BATCAT', 'marketcap': 3271345.920505294, 'num_of_whales': 0, 'num_of_holders': 9}, {'address': '6g5SypqztRMcsre1xdaKiLogcAzQ9ihfFUGndaAnos3W', 'symbol': 'Starbase', 'marketcap': 6084888.951087737, 'num_of_whales': 0, 'num_of_holders': 0}]

    # 3. Mix in AI formulation
    console.log("3. Mix in AI formulation ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    symbols = [t["symbol"] for t in tokens_for_x]
    ai_response = await generate_x_message(symbols, local = False)
    response_content = ai_response["choices"][0]['message']['content']
    as_json = extract_json(response_content)

    closing = as_json["closings"]
    closing = ['superhero squad mission incoming!', 'rocket fuel for cosmos!']
    """
    X whales just aped $BONK. The current MC is $XYZ
    """
    messages = []
    for i, token in enumerate(tokens_for_x):
        holders_message = ''
        if token['num_of_whales'] > 0:
            holders_message += f"{token['num_of_whales']} whales"
        elif token['num_of_holders'] > 0:
            holders_message += f"{token['num_of_holders']} smart wallets"
        message = f"{holders_message} have aped ${token['symbol']}. The current MC is ${token['marketcap']}, {closing[i]}."
        message += message + f"\n\n Munki"
        messages.append(message)


    # 4. Post to X
    console.log("4. Post to X ---------------------------------------------------------------------------------------------------------")  # fmt: skip
#     message = """9 smart wallets just aped $BATCAT. The current MC is $3.271m, superhero squad mission incoming!

# MUNKI"""
#     post_tweet(message)


if __name__ == "__main__":
    asyncio.run(init())

# python -m backend.xBot.x_bot
