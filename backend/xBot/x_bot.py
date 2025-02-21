import asyncio
import time
from typing import Any, Tuple

from dotenv import load_dotenv
import httpx
from backend.bot.parser import format_number
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.utils.api.birdeye_api_service import birdeyeApiService
from backend.commands.utils.api.entities.token_entities import TokenEntity, TrendingTokenEntity, TrendingTokenForX, TrendingTokenForXAnlysis
from backend.commands.utils.api.x_api_service import post_tweet
from backend.commands.utils.services.log_service import LogService
from backend.database.trending_token_entities_database import trendingTokenEntityDatabase
from backend.database.utils.db_string import upper_first_letter
from backend.xBot.x_bot_utils import exists_json, extract_json, get_amount_of_whales, get_from_json, get_name_symbol_address, save_to_json
from .x_openrouter_api import generate_x_message
import backend.xBot.x_bot_utils as x_bot_utils

load_dotenv()

logger = LogService("XBOT")
console = logger

# Threshold values for filtering tokens
# |Volume (24h)| MC |Holders|Whales|Created|
# |------------| -- |-------|------|-------|
# | 10,000,000 | 1m | 2,000 | 10   |24h ago|
# | 1,000,000  | 1m | 1,000 | 7    |24h ago|
# | 500,000    | 1m | 500   | 5    |24h ago|

THRESHOLD_ONE = {
    "marketcap": 1_000_000,
    "volume24hUSD": 10_000_000,
    "holder": 2_000,
    "whales": 10,
    "created": int((time.time() - 24 * 60 * 60))
}
THRESHOLD_TWO = {
    "marketcap": 1_000_000,
    "volume24hUSD": 1_000_000,
    "holder": 1_000,
    "whales": 7,
    "created": int((time.time() - 24 * 60 * 60))
}
THRESHOLD_THREE = {
    "marketcap": 1_000_000,
    "volume24hUSD": 500_000,
    "holder": 500,
    "whales": 5,
    "created": int((time.time() - 24 * 60 * 60)),
}
# THRESHOLD = THRESHOLD_ONE
# THRESHOLD = THRESHOLD_TWO
THRESHOLD = THRESHOLD_THREE

TRENDING_TOKENS_AMOUNT = 5
FETCH_LIMIT = 20
OFFSET_START = 0
OFFSET_LIMIT = OFFSET_START + 1000
# OFFSET_LIMIT = FETCH_LIMIT
TOP_HOLDER_AMOUNT = 50
MINIMUM_DOLLAR_AMOUNT = 10

async def get_trending_tokens(limit = TRENDING_TOKENS_AMOUNT) -> list[TrendingTokenEntity]:
    console.log(" START ----- 1.1.1 Get trending tokens ----------------------------------------------------------------------------------------------")  # fmt: skip
    filtered_trending_tokens: list[TrendingTokenForX] = []
    offset = OFFSET_START
    while len(filtered_trending_tokens) < limit:
        if offset >= OFFSET_LIMIT:
            break
        trending_tokens_response = await birdeyeApiService.get_trending_list({"limit":FETCH_LIMIT, "offset":offset})
        if not trending_tokens_response["success"]:
            return

        trending_tokens: list[TrendingTokenEntity] = trending_tokens_response["data"]["tokens"]
        save_to_json(trending_tokens, "x_bot/1_1_1_trending_token")
        save_to_json(get_name_symbol_address(trending_tokens), "x_bot/1_1_1_trending_token_short")
        # trending_tokens: list[TrendingTokenEntity] = trendingTokenEntityDatabase.fetch_all()
        console.log(" ----- 1.1.2 Filter by volume and mc ----------------------------------------------------------------------------------------------")  # fmt: skip
        filtered_by_mc: list[TrendingTokenEntity] = list(
            filter(lambda t: (t['marketcap'] > THRESHOLD['marketcap']), trending_tokens)
        )
        filtered_by_volume: list[TrendingTokenEntity] = list(
            filter(lambda t: (t['marketcap'] > THRESHOLD['marketcap']), filtered_by_mc)
        )
        save_to_json(filtered_by_volume, "x_bot/1_1_2_filtered_by_volume_and_mc")
        # filtered_by_volume_and_mc = trending_tokens
        console.log(" ----- 1.1.3 Filter by time ----------------------------------------------------------------------------------------------")  # fmt: skip
        filtered_by_time = await get_filtered_by_time(filtered_by_volume)
        save_to_json(filtered_trending_tokens, "x_bot/1_1_3_filtered_by_time")
        console.log(" ----- 1.1.4 Filter by holders ----------------------------------------------------------------------------------------------")  # fmt: skip
        filtered_by_holders = await get_filtered_by_holders(filtered_by_time)
        save_to_json(filtered_trending_tokens, "x_bot/1_1_4_filtered_by_holders")
        filtered_trending_tokens.extend([
            TrendingTokenForX(address=t['address'], symbol=t["symbol"], marketcap=t["marketcap"])
            for t in filtered_by_holders
        ])

        offset += FETCH_LIMIT
        console.log('>>>> _ >>>> ~ file: x_bot.py:80 ~ offset:', offset)  # fmt: skip

    console.log(" END ----- 1.1.1 Get trending tokens ----------------------------------------------------------------------------------------------")  # fmt: skip
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
                and token_creation_info["data"]["blockUnixTime"] > THRESHOLD["created"]
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
                and token_overview["data"]["holder"] > THRESHOLD["holder"]
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

async def get_trending_tokens_with_holders(address: str, local = False, log_to_client: Any = None) -> TrendingTokenForXAnlysis:
    console.log(" ----- 1.1 Get trending tokens with holders ----------------------------------------------------------------------------------------------")  # fmt: skip
    console.log('>>>> _ >>>> ~ file: x_bot.py:164 ~ address:', address)  # fmt: skip
    trending_tokens: list[Any] = []
    if local and exists_json("x_bot/1_1_trending_tokens_with_holders"):
        trending_tokens = get_from_json("x_bot/1_1_trending_tokens_with_holders")
    elif address:
        token_overview_response = await birdeyeApiService.get_token_overview(address)
        if token_overview_response:
            converted = TrendingTokenForXAnlysis().convert_from_overview(token_overview_response['data'])
            symbol = "N/A"
            if converted["symbol"]:
                symbol = converted["symbol"]
            if converted:
                trending_tokens = [converted]
                await log_to_client(f"Checking on {symbol.strip()} for ya...")
    else:
        trending_tokens = await get_trending_tokens()
    if trending_tokens == None:
        return

    save_to_json(trending_tokens, "x_bot/1_1_trending_tokens_with_holders")

    # 2. Call /top on tokens from (1.)
    console.log(" ----- 1.2 Get top holders for tokens from (1.) ----------------------------------------------------------------------------------------------")  # fmt: skip
    trending_tokens_with_holders: list[TrendingTokenForX] = []
    if local and exists_json("x_bot/1_2_2_tokens_for_with_holders"):
        trending_tokens_with_holders = get_from_json("x_bot/1_2_2_tokens_for_with_holders")
    else:
        for token in trending_tokens:
            top_holders_holdings = []
            if local and exists_json("x_bot/1_2_1_top_holders_holdings"):
                top_holders_holdings = get_from_json("x_bot/1_2_1_top_holders_holdings")
            else:
                top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=TOP_HOLDER_AMOUNT)
                # top_holders_holdings = await get_top_holders_holdings(token=token["address"], limit=0) # =0 for debugging, returns json
                save_to_json(top_holders_holdings, "x_bot/1_2_1_top_holders_holdings")

            if top_holders_holdings == None:
                continue

            amount_of_whales = get_amount_of_whales(top_holders_holdings)
            if amount_of_whales >= THRESHOLD['whales']:
                potential = {
                    "address": token["address"],
                    "symbol": token["symbol"],
                    "marketcap": token["marketcap"],
                    "num_of_whales": amount_of_whales
                }
                trending_tokens_with_holders.append(potential)
                await log_to_client(f"WHALES FOUND: >>{amount_of_whales}<<, weeeeeeeeeee")
            else:
                await log_to_client(f"{amount_of_whales} whales?! Not enough for the threshold: {THRESHOLD['whales']}")

        save_to_json(trending_tokens_with_holders, "x_bot/1_2_2_tokens_for_with_holders")

    # trending_tokens_with_holders=[{'address': '4MpXgiYj9nEvN1xZYZ4qgB6zq5r2JMRy54WaQu5fpump', 'symbol': 'BATCAT', 'marketcap': 3271345.920505294, 'num_of_whales': 0}, {'address': '6g5SypqztRMcsre1xdaKiLogcAzQ9ihfFUGndaAnos3W', 'symbol': 'Starbase', 'marketcap': 6084888.951087737, 'num_of_whales': 0}]
    return trending_tokens_with_holders

async def mix_in_ai(tokens: TrendingTokenForXAnlysis, local = False, log_to_client: Any = None) -> list[Tuple[str, bool]]:
    console.log(" ----- 2. Mix in AI formulation ----------------------------------------------------------------------------------------------")  # fmt: skip
    messages = []
    if local and exists_json("x_bot/2_mix_in_ai"):
        messages = get_from_json("x_bot/2_mix_in_ai")
    elif len(tokens):
        symbols = [t["symbol"] for t in tokens]
        await log_to_client("Engaging ROBOT MUNKI")
        ai_response = await generate_x_message(symbols)
        response_content = ai_response["choices"][0]['message']['content']

        closing_list: list[str] = []
        try:
            as_json = extract_json(response_content)
            closing_list = as_json["closings"]
        except Exception as exception:
            closing_list = ["" for _ in tokens]
            console.log('>>>> _ >>>> ~ file: x_bot.py:233 ~ exception:', exception)  # fmt: skip
            console.log(("[[vvvvvvvvvvvvvvvvvvvvvvvvvvv]]", False))
            console.log(("[[Sorry, there was an error parsing the AI response. Here is the raw text:]]", False))
            console.log((response_content, False))
            console.log(("[[^^^^^^^^^^^^^^^^^^^^^^^^^^^]]", False))

        """
        X whales just aped $BONK. The current MC is $XYZ
        """
        for i, token in enumerate(tokens):
            holders_message = f"{token['num_of_whales']} whales"
            mc = format_number(token['marketcap'], escape=False)
            symbol = token['symbol'].strip()
            symbol_symybol = '$'
            console.log('len symbol:', len(symbol))  # fmt: skip
            if len(symbol) > 6:
                symbol_symybol = '#'
            closing = ''
            if len(closing_list) == len(tokens):
                closing += ' ' + closing_list[i]
                closing = upper_first_letter(closing)
            message = f"{holders_message} have aped {symbol_symybol}{symbol}, the current MC is {mc}.{closing}"
            message += "\n\n Munki"
            messages.append((message, True))

        save_to_json(messages, "x_bot/2_mix_in_ai")

    return messages

async def default_log_to_client(message: str):
    console.log(message)

async def process_ca_and_post_to_x(address: str = None, limit = None, local = False, log_to_client: Any = default_log_to_client):
    x_bot_utils.log_tracker_map = {}
    """
    Process tokens and post to X.
    - If no address is provided, get trending tokens.
    - If address is provided, get token info.
    """
    # 1. Get trending tokens
    trending_tokens_with_holders = await get_trending_tokens_with_holders(address, log_to_client = log_to_client, local = local)


    # 2. Mix in AI formulation
    messages = await mix_in_ai(trending_tokens_with_holders, local, log_to_client)
    console.log('>>>> _ >>>> ~ file: x_bot.py:241 ~ messages:', messages)  # fmt: skip

    # 3. Post to X
    if len(messages):
        console.log(" ----- 3. Post to X ----------------------------------------------------------------------------------------------")
#     message = """9 smart wallets just aped $BATCAT. The current MC is $3.271m, superhero squad mission incoming!

# MUNKI"""
        # post_tweet(message)

    return messages


if __name__ == "__main__":
    asyncio.run(process_ca_and_post_to_x("9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump", local = True))
    # asyncio.run(process_ca_and_post_to_x())

# python -m backend.xBot.x_bot
