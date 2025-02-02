import asyncio
import json
import httpx
import itertools
import os
import random
import requests
import time

from solana.rpc.api import Client
from solders.pubkey import Pubkey

# heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get("solrpc")
quicknoderpc1 = os.environ.get("solrpc1")
quicknoderpc2 = os.environ.get("solrpc2")
quicknoderpc3 = os.environ.get("solrpc3")
quicknoderpc4 = os.environ.get("solrpc4")
# heliusrpc1 = os.environ.get('heliusrpc1')
birdeyeapi = os.environ.get("birdeyeapi")

# List of available RPCs
rpc_list = [quicknoderpc, quicknoderpc1, quicknoderpc2, quicknoderpc3, quicknoderpc4]
rpc_iterator = itertools.cycle(rpc_list)

# Solana RPC endpoint
solana_client = Client("https://api.mainnet-beta.solana.com")


async def get_rpc():
    global rpc_iterator
    return next(rpc_iterator)


class SolanaApiService:
    def __init__(self):
        self.solana_client = solana_client

    async def get_token_supply(token: str = None) -> float:
        """
        Get the total supply of a token
        Costs 0 credits per request
        // Originally from `token_utils.py`
        """
        print("Getting total supply for", token)
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "method": "getTokenSupply",
            "params": [token],
            "id": 1,
        }

        response = requests.post(await get_rpc(), headers=headers, json=data)
        if response.status_code != 200:
            return None
        if response.status_code != 200:
            return None
        print("Returning total supply for", token)
        return float(response.json()["result"]["value"]["uiAmount"])

    async def get_tx(signature: str):
        """
        Originally from `general_utils.py`
        """
        url = "https://fluent-dry-water.solana-mainnet.quiknode.pro/da1fa2655346449c8e2b4623b4f0c11775770de6/"
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0},
            ],
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            print("Error getting transaction: ", e)
            return None

    async def get_balance(
        wallet: str, token: str = None, client: httpx.AsyncClient = None
    ):
        timeout = 0.25

        """
        Get the balance of a wallet in SOL or a token
        Originally from `wallet_utils.py`
        """
        if token:
            print("Getting balance for", wallet, "in", token)
        else:
            print("Getting balance for", wallet, "in SOL")

        headers = {"Content-Type": "application/json"}
        if token:
            # Get token balance
            data = {
                "jsonrpc": "2.0",
                "method": "getTokenAccountsByOwner",
                "params": [wallet, {"mint": token}, {"encoding": "jsonParsed"}],
                "id": 1,
            }
        else:
            # Get SOL balance
            data = {
                "jsonrpc": "2.0",
                "method": "getBalance",
                "params": [wallet],
                "id": 1,
            }

        try:
            if client is None:
                response = requests.post(
                    await get_rpc(), headers=headers, json=data, timeout=timeout
                )
            else:
                response = await client.post(
                    await get_rpc(), headers=headers, json=data, timeout=timeout
                )
        except Exception as e:
            print("Error getting balance for", wallet, "in", token, ":Solana RPC")
            return None

        if response.status_code != 200:
            return None

        if token:
            result = response.json().get("result", {}).get("value", [])
            if not result:
                if token == "So11111111111111111111111111111111111111112":
                    return await get_balance(wallet=wallet)  # Get SOL balance
                return 0  # No token balance
            token_amount = float(
                result[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"]
            )
            decimals = result[0]["account"]["data"]["parsed"]["info"]["tokenAmount"][
                "decimals"
            ]
            if token == "So11111111111111111111111111111111111111112":
                return token_amount / (10**decimals) + await get_balance(
                    wallet=wallet
                )  # Convert lamports to SOL
            return token_amount / (10**decimals)
        else:
            balance = response.json().get("result", {}).get("value", 0)
            return balance / (10**9)  # Convert lamports to SOL

    def check_balance(wallet_address):
        try:
            # Convert the string address to a PublicKey object
            public_key = Pubkey.from_string(wallet_address)
        except ValueError as e:
            print(f"Invalid Solana wallet address. Error: {e}")
            return

        # Get account info
        account_info = solana_client.get_account_info(public_key)
        payed = 0

        if account_info.value is None:
            response = f"Balance for wallet is 0 SOL. Please transfer SOL or wait for transaction to finish and check again"
            return response, payed

        # Get balance in lamports and convert to SOL
        balance_in_lamports = account_info.value.lamports
        balance_in_sol = balance_in_lamports / 10**9  # Convert lamports to SOL

        # Format and send the response
        response = f"Balance for wallet {wallet_address}: {balance_in_sol} SOL "
        if balance_in_sol < 0.69:
            remaining_sol = 0.69 - balance_in_sol
            response = (
                response
                + f"Please transfer {remaining_sol} SOL and check again to unlock features"
            )
            return response, payed

        else:
            response = "Happy Trading! the features are now unlocked"
            payed = 1
            # Store this in a database or cache system
            return response, payed
