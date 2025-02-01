import asyncio
import json
import httpx
import os
import requests
import time

from .entities.api_entity import ApiResponse
from .entities.historical_price_unix_entity import HistoricalPriceUnixEntity
from .entities.token_overview_entity import TokenOverviewEntity
from ..services.log_service import LogService

birdeyeapi = os.environ.get("birdeyeapi")
CHAIN = "solana"
BASE_URL = "https://public-api.birdeye.so"

SEMAPHORE_NUM = 10
REQUEST_SEMAPHORE = asyncio.Semaphore(SEMAPHORE_NUM)

logger = LogService()

BIRDEYE_API_ENDPOINTS = {
    "historical_price_unix": "defi/historical_price_unix",
    "history_price": "defi/history_price",
    "token_overview": "defi/token_overview",
    "token_holder": "defi/v3/token/holder",
    "token_creation_info": "defi/token_creation_info",
    "gainers_losers": "trader/gainers-losers",
    "wallet_token_list": "v1/wallet/token_list",
    "wallet_token_balance": "v1/wallet/token_balance",
}


class BirdeyeApiService:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "chain": CHAIN,
            "X-API-KEY": birdeyeapi,
        }

    """
    ===========================================       ===========================================
    =========================================== PRICE ===========================================
    ===========================================       ===========================================
    """

    async def get_price(
        self, token: str = None, unix_time: int = None
    ) -> ApiResponse[HistoricalPriceUnixEntity]:
        """
        Get the price of a token at a given unix time, costs 5 credits per request
        """
        logger.log("Getting price for", token, "at", unix_time)
        if unix_time is None:
            unix_time = int(time.time())
        if token is None:
            token = "So11111111111111111111111111111111111111112"
        params = dict_to_query_params({"address": token, "unixtime": unix_time})
        url = f"{BASE_URL}/defi/historical_price_unix?{params}"
        try:
            response = requests.get(url, headers=self.headers)
        except:
            logger.log("Error getting price for", token, "at", unix_time, ":Birdeye")
            return None
        if response.status_code != 200:
            if response.json()["success"] == False:
                return None
        return response.json()["data"]["value"]

    async def get_price_historical(
        self, token: str = None, type: str = None, start: int = None, end: int = None
    ):
        logger.log("Getting price historical for", token, "from", start, "to", end)
        """
        Get the price of a token at a given unix time, costs 5 credits per request
        """
        type = "1m"
        params = dict_to_query_params(
            {
                "address": token,
                "address_type": "token",
                "type": type,
                "time_from": start,
                "time_to": end,
            }
        )
        url = f"{BASE_URL}/defi/history_price?{params}"
        try:
            response = requests.get(url, headers=self.headers)
        except:
            logger.log( "Error getting price historical for", token, "from", start, "to", end, ":Birdeye",)  # fmt: skip
            return None
        if response.status_code != 200:
            if response.json()["success"] == False:
                return None
        return response.json()["data"]["items"]

    """
    ===========================================        ===========================================
    =========================================== TRADER ===========================================
    ===========================================        ===========================================
    """

    async def get_top_traders(self, type: str = "1W", limit: int = 10000):
        """
        Costs 30 per call
        """
        logger.log(f"Getting top {limit} for {type}")
        # if(limit == 0): #for testing
        #     array_of_objects = ast.literal_eval(example_output)
        #     # Convert each dictionary in the list to a JSON string
        #     array_of_json = [json.dumps(d) for d in array_of_objects]
        #     return array_of_json
        all_data = {}
        if os.path.exists("top_traders.json"):
            with open("top_traders.json", "r") as file:
                try:
                    all_data = json.load(file)
                except json.JSONDecodeError:
                    logger.log( "Error loading 'top_traders.json'. File is empty or corrupt.")  # fmt: skip
                    all_data = {}
                for item in all_data.get("items", []):
                    if (
                        int(time.time() - item.get("timestamp", 0)) < 7 * 24 * 60 * 60
                    ) and (item.get("type", "") == type):
                        logger.log("Returning cached data from 'top_traders.json'.")
                        return item.get("items", [])
        res = []
        while len(res) < limit:

            params = dict_to_query_params(
                {
                    "type": type,
                    "sort_by": "PnL",
                    "sort_type": "desc",
                    "offset": len(res),
                    "limit": 10,
                }
            )
            url = f"{BASE_URL}/trader/gainers-losers?{params}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.log("Error getting top traders: ", response.json())
                return res
            res += response.json()["data"]["items"]
        current_timestamp = str(int(time.time()))
        try:
            if "items" not in all_data:
                all_data["items"] = []
            all_data["items"].append(
                {
                    "timestamp": int(current_timestamp),
                    "type": type,
                    "limit": limit,
                    "items": res,
                }
            )
        except NameError:
            logger.log("Creating new saved_data dictionary.")
        try:
            with open("top_traders.json", "w") as file:
                json.dump(all_data, file, indent=4)
            logger.log(
                f"Saved top {len(res)} traders for {type} to 'top_traders.json'."
            )
        except Exception as e:
            logger.log(f"Error saving to 'top_traders.json': {e}")
        logger.log("Returning top {} traders for {}".format(limit, type))
        return res

    async def get_wallet_trade_history(
        self, wallet: str, limit: int = 100, before_time: int = 0, after_time: int = 0
    ):

        if limit == 0:
            if os.path.exists("trade_history.json"):
                with open("trade_history.json", "r") as file:
                    data = json.load(file)
                    print("Returning cached data from 'trade_history.json'.")
                    return data
        print("Getting trade history for", wallet)
        res = []
        while len(res) < limit:
            params = dict_to_query_params(
                {
                    "address": wallet,
                    "offset": len(res),
                    "limit": 100,
                    "tx_type": "swap",
                    "before_time": before_time,
                    "after_time": after_time,
                }
            )
            url = f"{BASE_URL}/trader/txs/seek_by_time?{params}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print("Error getting trade_history: ", response.json())
                return res
            res += response.json()["data"]["items"]
            if len(response.json()["data"]["items"]) < 100:
                break
        # try:
        #     with open('trade_history.json', 'w') as file:
        #         json.dump(res, file, indent=4)
        #     print(f"Saved trade history for {wallet} to 'trade_history.json'.")
        # except Exception as e:
        #     print(f"Error saving to 'top_holders.json': {e}")
        print("Returning trade history for", wallet)
        return res

    """
    ===========================================       ===========================================
    =========================================== TOKEN ===========================================
    ===========================================       ===========================================
    """

    async def get_token_overview(
        self, token: str = None
    ) -> ApiResponse[TokenOverviewEntity]:
        """
        https://docs.birdeye.so/reference/get_defi-token-overview
        Get the overview of a token
        Costs 20 credits per request
        """
        logger.log("Getting token overview for", token)
        if token is None:
            return None

        params = dict_to_query_params({"address": token})
        url = f"{BASE_URL}/defi/token_overview?{params}"
        response = requests.get(url, headers=self.headers)
        logger.log("Returning token overview for", token)
        return response.json()

    async def get_top_holders_with_constraint(
        self, token: str = None, min_value_usd: float = None, price: float = None
    ):
        """
        Get the top holders of a token that hold at least min_value_usd worth of tokens

        Args:
            token (str): Token address
            min_value_usd (float): Minimum USD value of tokens that a holder must have
            price (float): Current price of token in USD

        Returns:
            list: List of holders that meet the minimum value constraint
        """
        if token is None:
            return None

        if min_value_usd is None or price is None:
            return None

        all_holders = []
        offset = 0
        batch_size = 100

        while True:
            params = dict_to_query_params(
                {
                    "address": token,
                    "offset": offset,
                    "limit": batch_size,
                }
            )
            url = f"{BASE_URL}/defi/v3/token/holder?{params}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                if not response.json()["success"]:
                    return None

            batch = response.json()["data"]["items"]

            # Stop if we hit empty batch or zero amounts
            if not batch or batch[0]["amount"] == "0" or batch[-1]["amount"] == "0":
                break

            # Filter holders that meet minimum value
            for holder in batch:
                value_usd = float(holder["uiAmount"]) * price
                if value_usd >= min_value_usd:
                    all_holders.append(holder)
                else:
                    # Since holders are ordered by amount, we can stop once we hit one below threshold
                    return all_holders

            offset += batch_size

        return all_holders

    async def get_token_creation_info(self, token: str = None):
        """{
        "data": {
            "txHash": "4ePtuFmo3uYX5m2mqMYEVqUpJzCoRHymmrTnCk1q1KiyvhpmCABVQ1sq1CFLMWHZAwbicC8V1Ao664WumAqxWQ86",
            "slot": 306705009,
            "tokenAddress": "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump",
            "decimals": 6,
            "owner": "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM",
            "blockUnixTime": 1733878974,
            "blockHumanTime": "2024-12-11T01:02:54.000Z"
        },"success": true}
        """
        logger.log("Getting token creation info for", token)

        params = dict_to_query_params({"address": token})
        url = f"{BASE_URL}/defi/token_creation_info?{params}"

        try:
            response = requests.get(url, headers=self.headers)
            return response.json()["data"]
        except Exception as e:
            logger.log("Error getting token creation info for", token, ":Birdeye")
            return None

    async def get_top_holders(self, token: str = None, limit=None):
        """
        Get the top holders of a token, costs 50 credits per request
        Iterates through all holders using offset pagination
        """
        logger.log("Getting top holders for", token, "with limit", limit)
        if limit == 0:
            if os.path.exists("top_holders.json"):
                with open("top_holders.json", "r") as file:
                    logger.log("Returning cached data from 'top_holders.json'")
                    return json.load(file)
        all_holders = []
        if token is None:
            return True

        offset = 0
        batch_size = 100 if limit is None or limit > 100 else limit
        res = []

        while True:
            url = f"{BASE_URL}/defi/v3/token/holder?address={token}&offset={offset}&limit={batch_size}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                if response.json()["success"] == False:
                    return None
            batch = response.json()["data"]["items"]
            if (
                not batch
                or batch[0]["amount"] == "0"
                or batch[len(batch) - 1]["amount"] == "0"
            ):
                if len(all_holders) == 0:
                    all_holders.extend(batch)
                break
            # logger.log(len(batch))
            all_holders.extend(batch)
            # If we have a limit and reached/exceeded it, trim and break
            if limit is not None and len(all_holders) >= limit:
                all_holders = all_holders[:limit]
                break
            # If this batch was smaller than requested, we've got all holders
            if len(batch) < batch_size:
                break
            # Only continue if we need all holders
            if limit is None or len(all_holders) < limit:
                offset += batch_size
            else:
                break
        for holder in all_holders:
            res.append(holder["owner"])
        try:
            with open("top_holders.json", "w") as file:
                json.dump(all_holders, file, indent=4)
            logger.log(
                f"Saved top {len(res)} holders for {type} to 'top_holders.json'."
            )
        except Exception as e:
            logger.log(f"Error saving to 'top_holders.json': {e}")
        logger.log("Returning top holders for", token)
        logger.log("Returned", len(all_holders), "holders")
        return all_holders

    """
    ===========================================        ===========================================
    =========================================== WALLET ===========================================
    ===========================================        ===========================================
    """

    async def get_wallet_token_list(
        self, address: str, session: httpx.AsyncClient = None
    ):
        """
        https://docs.birdeye.so/reference/get_defi-tokenlist

        Get token list with rate limiting and error handling

        :param address: Wallet address to fetch portfolio for
        :param session: Shared HTTP client session
        :return: Portfolio data or error dict
        """
        url = f"{BASE_URL}/v1/wallet/token_list?wallet={address}"
        async with REQUEST_SEMAPHORE:
            try:
                fetch = session or requests
                response = await fetch.get(url, headers=self.headers)

                if response.status_code != 200:
                    return {"error": f"Failed to fetch portfolio for wallet {address}"}

                data = response.json()["data"]

                if not data.get("success", True):
                    return {"error": f"Failed to fetch portfolio for wallet {address}"}
                logger.log(f"Fetched portfolio for wallet {address}")
                return data
            except Exception as e:
                return {
                    "error": f"Exception fetching portfolio for wallet {address}: {str(e)}"
                }

    async def get_balance_birdeye(self, wallet, token):
        print("Getting balance using Birdeye for", wallet, "in", token)

        url = (
            f"{BASE_URL}/v1/wallet/token_balance?wallet={wallet}&token_address={token}"
        )

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return None
            data = response.json()["data"]
            print(f"Fetched balance for wallet {wallet} in {token}")
            return data
        except Exception as e:
            print(
                f"Error fetching balance using Birdeye for wallet {wallet} in {token}: {str(e)}"
            )
            return None


def dict_to_query_params(params: dict) -> str:
    """
    Convert a dictionary to a query parameter string.

    Args:
        params (dict): Dictionary of query parameters.

    Returns:
        str: Query parameter string.

    Example:
        >>> dict_to_query_params({"key1": "value1", "key2": "value2"})
        'key1=value1&key2=value2'
    """
    return "&".join(f"{key}={value}" for key, value in params.items())


if __name__ == "__main__":

    async def call():
        service = BirdeyeApiService()
        response = await service.get_token_overview(
            "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"
        )
        response.data

    call()
