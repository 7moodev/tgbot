import requests
from token_helper import getRpc, getTopHolders, getTokenOverview, getTokenTotalSupply
import os
from wallet_helper import getWalletAvgPrice
import asyncio
birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
solscanapi = os.environ.get('solscan')




async def getHolderAvgBuyPrice(token: str, limit: int):
    """
    Get the average buy price of a token for a given wallet
    """
    holders = await getTopHolders(token, limit)
    token_info = await getTokenOverview(token)
    tokenOverview = await getTokenOverview(token)
    if tokenOverview:
        tokenOverview = tokenOverview['data']
        symbol = tokenOverview['symbol']
        name = tokenOverview['name']
        logoUrl = tokenOverview['logoURI']
        liquidity = tokenOverview['liquidity']
        marketCap = tokenOverview['mc']
        #more info about the token
    else:
        tokenOverview = None
    token_info = {
        'symbol': symbol,
        'name': name,
        'logoUrl': logoUrl,
        'liquidity': liquidity,
        'marketCap': marketCap,
    }
    results = [token_info]
    avgBuyPriceSum = 0
    for holder in holders:
        avgBuyPrice = getWalletAvgPrice(holder['owner'], token, "buy")
        if avgBuyPrice:
            results.append({
                'address': holder['owner'],
                'avgBuyPrice': avgBuyPrice
            })
            avgBuyPriceSum += avgBuyPrice
        else:
            results.append({
                'address': holder['owner'],
                'avgBuyPrice': None
            })
    avgBuyPrice = avgBuyPriceSum / len(holders)
    results.append({
        'avgBuyPrice': avgBuyPrice
    })
    return results




if __name__ == "__main__":
    print(asyncio.run(getHolderAvgBuyPrice("7FhLDYhLagEYx8mvheyWMo25ChQcM9F54TiM15Ydpump", 10)))