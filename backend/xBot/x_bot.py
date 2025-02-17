import asyncio
import time
from typing import Any

from dotenv import load_dotenv
import httpx
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.token_entities import TokenEntity, TrendingTokenEntity, TrendingTokenForX, TrendingTokenForXAnlysis
from backend.commands.utils.api.x_api_service import post_tweet
from backend.commands.utils.services.log_service import LogService
from backend.database.trending_token_entities_database import trendingTokenEntityDatabase
from backend.xBot.x_bot_utils import exists_json, get_amount_of_whales, get_from_json, save_to_json
from .x_openrouter_api import generate_x_message

load_dotenv()

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
OFFSET_LIMIT = 300
# OFFSET_LIMIT = FETCH_LIMIT
TOP_HOLDER_AMOUNT = 50
MINIMUM_DOLLAR_AMOUNT = 10

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

    return filtered_trending_tokens

async def get_filtered_by_time(tokens: list[TrendingTokenEntity]) -> list[TrendingTokenEntity]:
    async with httpx.AsyncClient() as session:
        birdeyeApiService.with_session(session)

        async def get_creation_info(token: TokenEntity):
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

        async def get_token_overview(token: TokenEntity):
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

async def get_trending_tokens_with_holders(address: str, local = False) -> TrendingTokenForXAnlysis:
    console.log("1.1 Get trending tokens ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    console.log('>>>> _ >>>> ~ file: x_bot.py:195 ~ address:', address)  # fmt: skip
    trending_tokens: list[Any] = []
    if local and exists_json("x_bot/1_trending_tokens"):
        trending_tokens = get_from_json("x_bot/1_trending_tokens")
    elif address:
        token_overview_response = await birdeyeApiService.get_token_overview(address)
        if token_overview_response:
            converted = TrendingTokenForXAnlysis().convert_from_overview(token_overview_response['data'])
            if converted:
                trending_tokens = [converted]
        pass
    else:
        trending_tokens = await get_trending_tokens()
    if trending_tokens == None:
        return

    save_to_json(trending_tokens, "x_bot/1_trending_tokens")

    # 2. Call /top on tokens from (1.)
    console.log("1.2 Call /top on tokens from (1.) ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    tokens_for_x: list[TrendingTokenForX] = []
    if False and local and exists_json("x_bot/2_tokens_for_x"):
        trending_tokens = get_from_json("x_bot/2_tokens_for_x")
    else:
        amount_of_holders_list = []
        for token in trending_tokens:
            top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=TOP_HOLDER_AMOUNT)
            # top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=0) # =0 for debugging, returns json
            if top_holders_holdings == None:
                continue
            amount_of_whales = get_amount_of_whales(top_holders_holdings)
            amount_of_holders_list.append(amount_of_whales)
        console.log('>>>> _ >>>> ~ file: x_bot.py:154 ~ amount_of_whales_list:', amount_of_holders_list)  # fmt: skip
        tokens_for_x: list[TrendingTokenForX] = [
            {
                "address": token["address"],
                "symbol": token["symbol"],
                "marketcap": token["marketcap"],
                "num_of_whales": amount_of_holders_list[i],
            }
            for i, token in enumerate(trending_tokens)
        ]
        tokens_for_x = [token for token in tokens_for_x if token["num_of_whales"] > 0]

    save_to_json(tokens_for_x, "x_bot/2_tokens_for_x")

    # tokens_for_x=[{'address': '4MpXgiYj9nEvN1xZYZ4qgB6zq5r2JMRy54WaQu5fpump', 'symbol': 'BATCAT', 'marketcap': 3271345.920505294, 'num_of_whales': 0}, {'address': '6g5SypqztRMcsre1xdaKiLogcAzQ9ihfFUGndaAnos3W', 'symbol': 'Starbase', 'marketcap': 6084888.951087737, 'num_of_whales': 0}]
    return tokens_for_x

async def mix_in_ai(tokens_for_x: TrendingTokenForXAnlysis, local = False) -> TrendingTokenForXAnlysis:
    console.log("2. Mix in AI formulation ---------------------------------------------------------------------------------------------------------")  # fmt: skip
    messages = []
    symbols = [t["symbol"] for t in tokens_for_x]
    if local and exists_json("x_bot/3_mix_in_ai"):
        messages = get_from_json("x_bot/3_mix_in_ai")
    elif len(symbols):
        ai_response = await generate_x_message(symbols, local = False)
        response_content = ai_response["choices"][0]['message']['content']
        as_json = extract_json(response_content)

        closing = as_json["closings"]
        closing = ['superhero squad mission incoming!', 'rocket fuel for cosmos!']
        """
        X whales just aped $BONK. The current MC is $XYZ
        """
        for i, token in enumerate(tokens_for_x):
            holders_message = ''
            if token['num_of_whales'] > 0:
                holders_message += f"{token['num_of_whales']} whales"
            message = f"{holders_message} have aped ${token['symbol']}. The current MC is ${token['marketcap']}, {closing[i]}."
            message += message + f"\n\n Munki"
            messages.append(message)

        save_to_json(messages, "x_bot/3_mix_in_ai")

    console.log('>>>> _ >>>> ~ file: x_bot.py:1 ~ messages:', messages)  # fmt: skip
    return messages

async def process_ca_and_post_to_x(address: str = None, local = False):
    """
    Process tokens and post to X.
    - If no address is provided, get trending tokens.
    - If address is provided, get token info.
    """
    # 1. Get trending tokens
    tokens_for_x = await get_trending_tokens_with_holders(address, local)

    # 2. Mix in AI formulation
    messages = await mix_in_ai(tokens_for_x, local)

    # 3. Post to X
    if len(messages):
        console.log("4. Post to X ---------------------------------------------------------------------------------------------------------")
#     message = """9 smart wallets just aped $BATCAT. The current MC is $3.271m, superhero squad mission incoming!

# MUNKI"""
        # post_tweet(message)


if __name__ == "__main__":
    # asyncio.run(process_ca_and_post_to_x("CfJ58KZpVvPm5ketxbUMmRMHZh41AWZh9qx8r9cspump", local = True))
    asyncio.run(process_ca_and_post_to_x())

# python -m backend.xBot.x_bot
