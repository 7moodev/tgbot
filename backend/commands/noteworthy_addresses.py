import os
from .utils.token_utils import get_token_supply, get_token_overview, get_top_holders
import httpx
import asyncio
from .utils.general_utils import get_top_traders
from .utils.token_utils import get_rpc, get_top_holders, get_token_overview, get_token_creation_info
from .utils.wallet_utils import  get_balance, get_wallet_portfolio
from .top_holders_holdings import get_top_holders_holdings
import time
import requests
import json
from typing import List, Dict, Any

# whales_file_path = "backend/commands/constants/whales.json"
# with open(whales_file_path, 'r') as f:  
#     whales = json.load(f)
#     whales = set(whales['items'])


async def get_noteworthy_addresses(token: str, limit: int=None):
    top_traders = await get_top_traders(type='1W', limit = limit) #to change to 10k
    res = []
    if limit == 0:
        with open ("backend/commands/outputs/top_holders_holdings.json", 'r') as f:
            top_holders_holdings = json.load(f)
    else:
        top_holders_holdings = await get_top_holders_holdings(token, limit=limit)
    for item in top_holders_holdings['items']:
        if 'error' in item:
            continue
        if item['net_worth_excluding'] > 50000:
            res.append(item)
        for trader in top_traders:
            if trader['address'] == item['wallet']:
                stats = {
                    'pnl': trader['pnl'],
                    'volume': trader['volume'],
                    'trade_count': trader['trade_count'] 
                }
                for appended in res:
                    if appended['wallet'] == item['wallet']:
                        appended['top_trader'] = stats
                        break
    #         
    return {
        'token_info': top_holders_holdings['token_info'],
        'valid_results': len(res),
        'items': res
    }
if __name__ == "__main__":
    timenow = float(time.time())
    wtf = asyncio.run(get_noteworthy_addresses("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump", 0))
    #print(wtf)
    print(float(time.time()) - timenow)
    with open("backend/commands/outputs/noteworthy_addresses.json", 'w') as f:  
        json.dump(wtf, f, indent=4)