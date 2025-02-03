import httpx
import os
import asyncio
from .utils.token_utils import get_rpc, get_top_holders, get_token_overview, get_token_creation_info, get_token_supply
from .utils.wallet_utils import get_wallet_age, calculate_avg_entry,calculate_avg_holding, get_wallet_trade_history, calculate_avg_exit, get_wallet_age_readable
import time
import json

async def get_holder_avg_entry_price(wallet:str ,token: str, token_creation_time: int = 0):
    print(f"Getting avg entry price of holder {wallet} for token", token)
    trade_history = await get_wallet_trade_history(wallet=wallet, limit = 1000, after_time=token_creation_time)#to change to limit
    if trade_history is None:
        return None, None, None
    if len(trade_history) == 0:
        return None, None, None
    avg_raw_entry_price = await calculate_avg_entry(token_address=token,data=trade_history)
    avg_raw_exit_price = await calculate_avg_exit(token_address=token, data=trade_history)
    avg_actual_holding_price = await calculate_avg_holding(avg_raw_entry_price, avg_raw_exit_price)
    print(f"Returning avg entry price of holder {wallet} for token", token)
    return avg_raw_entry_price, avg_raw_exit_price, avg_actual_holding_price

async def get_holders_avg_entry_price(token: str, limit:int):
    if limit == 0:
        with open("backend/commands/outputs/holders_avg_entry_price.json", 'r') as f:
            return json.load(f)
    total_supply = await get_token_supply(token)
    token_creation_info = await get_token_creation_info(token)
    token_overview = await get_token_overview(token)
    if token_overview:
        print(token_overview)
        token_overview = token_overview['data']
        token_info = {
            'price': token_overview['price'],
            'symbol': token_overview['symbol'],
            'name': token_overview['name'],
            'logoURI': token_overview['logoURI'],
            'liquidity': token_overview['liquidity'],
            'market_cap': token_overview['mc'],
            'supply': total_supply,
            'circulatingSupply': token_overview['circulatingSupply'],
            'realMc': token_overview['realMc'],
            'holder': token_overview['holder'],
            'extensions': token_overview['extensions'],
            'priceChange1hPercent': token_overview['priceChange1hPercent'],
        }
        if token_creation_info:
            token_info['creationTime'] = token_creation_info['blockUnixTime']
    else:
        token_info = {}
    top_holders = await get_top_holders(token, limit)
    dev = token_creation_info['owner']
    token_creation_time = token_creation_info['blockUnixTime']
    res = []
    counted = 0
    count = 0
    agg_avg_price = 0
    for holder in top_holders:
        holder_address = holder['owner']
        holding_amount = holder['ui_amount']
        
        avg_raw_entry_price, avg_raw_exit_price, avg_actual_holding_price = await get_holder_avg_entry_price(holder_address, token, token_creation_time)
        if avg_raw_entry_price is None:
                res.append({'count': count,'holder': holder_address,'holding': holding_amount,'label': 'No Trades/Funded', 'avg_raw_entry_price': None, 'avg_raw_exit_price': None, 'avg_actual_holding_price': None})
            #implement logic to check where the tokens came from
        if avg_actual_holding_price is not None:
            price = avg_actual_holding_price['avg_holding_price']
            label = avg_actual_holding_price['label']
            if label is None:
                if holding_amount > avg_actual_holding_price['current_holding_amount']:
                    label = 'Funded'
            if label == "Normal":
                counted+=1
                agg_avg_price+=price
            res.append({'count': count,'holder': holder_address,'holding': holding_amount,'label': label, 'avg_raw_entry_price': avg_raw_entry_price, 'avg_raw_exit_price': avg_raw_exit_price, 'avg_actual_holding_price': avg_actual_holding_price})
        count = count+1

        print(f"Returning {counted} holders with valid avg entry prices")
    with open("backend/commands/outputs/holders_avg_entry_price.json", 'w') as f:  
        json.dump({"token_info": token_info,"agg_avg": (agg_avg_price/counted), "items": res}, f, indent=4)
    return {"token_info": token_info,"agg_avg": (agg_avg_price/counted), "items": res}

if __name__ == "__main__":
    start_time = time.time()
    res = asyncio.run(get_holders_avg_entry_price("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump", 25))
    #Execution time: 9.242473602294922 seconds for 50 holders
    print(f"Execution time: {time.time() - start_time} seconds")
    with open("backend/commands/outputs/holders_avg_entry_price.json", 'w') as f:  
        json.dump(res, f, indent=4)
