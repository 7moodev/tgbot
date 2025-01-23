import os
from .utils.token_utils import get_token_supply, get_token_overview, get_top_holders
import httpx
import asyncio
from .utils.general_utils import get_top_traders
from .utils.token_utils import get_rpc, get_top_holders, get_token_overview, get_token_creation_info
from .utils.wallet_utils import get_wallet_avg_price_deprecated, get_balance
import time
import requests
import json

whales_file_path = "backend/commands/db/whales.json"
with open(whales_file_path, 'r') as f:  
    whales = json.load(f)
    whales = set(whales)

async def get_noteworthy_addresses(token: str, limit: int=None):
    # convention:
    # 0: Exchanges / Whales
    # 1: Top Trader
    # 2: dev
    token_creation_info = await get_token_creation_info(token)
    token_creation_time  = token_creation_info['blockUnixTime']
    dev_wallet = token_creation_info['owner']
    top_traders = await get_top_traders(limit) #to change to 10k
    total_supply = await get_token_supply(token)
    top_holders = await get_top_holders(token, limit) #to change to 1000
    #top_holders.append('2ehPA8DSamWyw1MdPCjC4RMNjarRvptm1B9wwbuyaFym')
    res = []
    hashSet = set()
    # Define an async helper to process a single wallet
    for index,holder in enumerate(top_holders):
        print(type(holder))
        print(holder)
        if holder['owner'] in whales:
            res.append({"type": 0, "address": holder, 'holderIdx': index})
        if holder['owner'] == dev_wallet:
            res.append({"type": 2, "address": holder, 'holderIdx': index})
        for trader in top_traders:
            if trader['address'] == holder:
                res.append({"type": 1, "address": holder, 'holderIdx': index, 'pnl': trader['pnl'], 'volume': trader['volume'], 
                            'trade_count': trader['trade_count']})
    return res
if __name__ == "__main__":
    wtf = asyncio.run(get_noteworthy_addresses("FUAfBo2jgks6gB4Z4LfZkqSZgzNucisEHqnNebaRxM1P", 1000))
    print(wtf)
    with open("wtf.json", 'w') as f:  
        json.dump(wtf, f, indent=4)
    