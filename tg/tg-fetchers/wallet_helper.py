import httpx
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from token_helper import getPrice, getPriceHistorical
from utils import getRpc, getWalletAge
from bisect import bisect_left
birdeyeapi = os.environ.get('birdeyeapi')
heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
solscanapi = os.environ.get('solscan')

async def getBalance(wallet: str, token: str = None, client: httpx.AsyncClient = None):

    """
    Get the balance of a wallet in SOL or a token
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
            "params": [
                wallet,
                {"mint": token},
                {"encoding": "jsonParsed"}
            ],
            "id": 1
        }
    else:
        # Get SOL balance
        data = {
            "jsonrpc": "2.0",
            "method": "getBalance",
            "params": [wallet],
            "id": 1
        }
    try:
        response = await client.post(getRpc(), headers=headers, json=data)
    except:
        print("Error getting balance for", wallet, "in", token, ":Solana RPC")
        return None

    if response.status_code != 200:
        return None

    if token:
        result = response.json().get('result', {}).get('value', [])
        if not result:
            return 0
        token_amount = float(result[0]['account']['data']['parsed']['info']['tokenAmount']['amount'])
        decimals = result[0]['account']['data']['parsed']['info']['tokenAmount']['decimals']
        return token_amount / (10 ** decimals)
    else:
        balance = response.json().get('result', {}).get('value', 0)
        return balance / (10 ** 9)  # Convert lamports to SOL

async def getWalletTradeHistory(wallet: str, token: str = None, activity_type: list[str] = None, client: httpx.AsyncClient = None):
    """
    Get the trade history of a wallet
    """
    page = 1
    headers = {"token": solscanapi}
    results = []
    if getWalletAge(wallet) == 0:
        return []
    while True:
        base_url = f"https://pro-api.solscan.io/v2.0/account/defi/activities?address={wallet}&page={page}&page_size=100"
        if token:
            base_url += f"&token={token}"
        if activity_type:
            for activity in activity_type:
                base_url += f"&activity_type[]={activity}"
        try:
            response = await client.get(base_url, headers=headers)
        except:
            print("Error getting trade history for", wallet, "in", token, ":Solscan")
            return []
        if response.status_code != 200:
            break

        data = response.json().get('data', [])
        if not data:
            break

        results.extend(data)
        if len(data) < 100:
            break

        page += 1

    return results

async def getWalletAvgPrice(wallet: str, token: str = None, side: str = None, client: httpx.AsyncClient = None):
    print("Getting average price for", wallet, "in", token)
    """
    Get the average buy price of a token for a given wallet
    """
    defi_activity_types = ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"]
    wallet_trade_history = await getWalletTradeHistory(wallet, token, defi_activity_types, client)
    if not wallet_trade_history:
        return None
    balance = await getBalance(wallet, token, client)
    sofar = 0
    print("Wallet", wallet, "has", len(wallet_trade_history), "buy transactions")
    if token is None:
        token = "So11111111111111111111111111111111111111112"
    if len(wallet_trade_history) > 6:
        prices = await getPriceHistorical(token, "1m", wallet_trade_history[-1]['block_time'], wallet_trade_history[0]['block_time'])
    else:
        prices = None
    counter = 0
    if wallet_trade_history:
        
        trade_size_x_price_sum = 0
        trade_size_sum = 0
        for activity in wallet_trade_history:
            print("Digging in entry:", f"{counter}/{len(wallet_trade_history)}")
            counter += 1
            try:
                if balance:
                    if sofar >= balance:
                        break
                block_time = activity['block_time']
                if prices: 
                    price = getPriceHistoricalHelper(prices, block_time)
                else:
                    price = await getPrice(token, block_time)
                if price is None:
                    continue
                if price:
                    print("Summing up")
                    routers = activity['routers']
                    if side == "buy" and routers['token2'] == token:
                        amount = routers['amount2'] / 10 ** routers['token2_decimals']
                        sofar += amount
                        trade_size_x_price_sum += price * amount
                        trade_size_sum += amount
                    elif side == "sell" and routers['token1'] == token:
                        amount = routers['amount1'] / 10 ** routers['token1_decimals']
                        trade_size_x_price_sum += price * amount
                        trade_size_sum += amount
                    print("Summed up")
            except Exception as e:
                print(e)
                continue
        try:
            toReturn =  trade_size_x_price_sum / trade_size_sum
            print("Returning", toReturn)
            return toReturn
        except ZeroDivisionError:
            return None
    return None


def getPriceHistoricalHelper(data, target_unix_time):
    print("Searching for price historical for", target_unix_time)
    # Extract the unixTime values into a sorted list
    unix_times = [entry['unixTime'] for entry in data]
    
    # Use binary search to find the closest index
    pos = bisect_left(unix_times, target_unix_time)

    # Determine the closest value by comparing neighbors
    if pos == 0:
        closest = unix_times[0]
    elif pos == len(unix_times):
        closest = unix_times[-1]
    else:
        before = unix_times[pos - 1]
        after = unix_times[pos]
        closest = before if abs(before - target_unix_time) <= abs(after - target_unix_time) else after

    # Find the corresponding entry in the data
    for entry in data:
        if entry['unixTime'] == closest:
            print("Found price historical for", target_unix_time, ":", entry['value'])
            return entry['value']
async def processWallet(wallet: str, client: httpx.AsyncClient):
    try:
        avg_price = await getWalletAvgPrice(wallet, "63EWLHRLxdjoa7VLMNHV9JvJTRNVMkELhUkZHPRhpump", "buy", client)
        print(f"Average price for wallet {wallet}: {avg_price}")
    except Exception as e:
        print(f"Error processing wallet {wallet}: {e}")

async def main():
    wallets = ['5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 'AM84n1iLdxgVTAyENBcLdjXoyvjentTbu5Q6EpKV1PeG', 'Ggn2LtCYqLjCDGExYTm5aduRNPR8WHPEFuA6nMH6rmbL',
                'FTg1gqW7vPm4kdU1LPM7JJnizbgPdRDy2PitKw6mY27j', 'BrShW7se5m5nCeupxsgMo6mcGHx256xUE756yqB6PnyC', 'AEiiScFekUardNBJQb64WRyzyGwATkvEgzyxwrkyhW9f',
                  'BWrpB3CcSGSmb45NksMffSehQ4QNuLEzUKnUgtvsfL6N', '59UiSXYNXaxd5jC3UWPc9HnXrWsCYuA8SP5ynqbv9fWV', 'ECCKBDWX3MkEcf3bULbLBb9FvrEQLsmPMFTKFpvjzqgP',
                    '6mNqs4W3UR4yynj3RWmVnQLMKpyma21Mw9ZcfBNwAg9V', '7Sdxwcy7ofpLkxCJaR6QzN4qu5V5gC8hKAe9FQfyHvMk', 'HSX1unkhjaLHmSd4XbPWoXay35YeS2RVGVeJBPKLTQd5',
                      '2u1DB7QMqFnRZ7MPggJQp7cPrfbjC3etgeppMm2kv2Zd', 'D6nUhQ7o3TQwk243mgVS5hsdkuJk71fxZib3KxY4Upyv', '8VsSMNYxwBQgspSbQ71w7eJfMSzALzdKKvgL3ozfntNs',
                        'D39mf52JoZVnCtksy7csG4xNsz5YAsXCHgyK5ERXJmmm', '62k95KmZ6yjQ3qhQMrvscd7yh6WEFqS7oRKLXmdmnoLM', 'HRnGiwh99qS6XfHMhRmyt8YWWtiNn3RjDoihHvqc6j8G',
                          'FaDjpoQFQqUE5m83yLY8gqp6dMgH6c4Xx8ucG33zdBrk', '9h8GYpAwYdqLwh3wHfrJYm2kKaxJo2sdjQ7QSncutLQi', '6zFuiktuEyyv2ug8n9rZXVKmeVgX8x2DuXBhuFfk8ynA',
                            'FtSyuMFEJni7bZUreq2xEiFGDKKdvAWTQ4WP2sbwnMdp', 'AypDMMLZK4joGQ8CJobFz6e8haVkBQafoGdrFM8H3yKM', '7sTgkPKiQg85qTi27aGWBcKsf8LZPufqQU5sA1KtNaV8',
                              'ELtz2XDg3BY3c2K3CiGTv6egyNRbhzzJhZFckCvQiz9y', '7PBXSnAYa2UeWmv9wp7sace5N43Hubpv9Ffuz4h5D7QQ', '39izaxgq6gR1Ma6Uh4vjGBpCUGXoehzgEqQ16Mh6wVBf',
                                'D8m6nVAYST9oiBqs2jZM4tZ7LbkL1rCDhcYyme3LsArr', '8VAh3N4sZ6WfweYGdSBw4aUt21TQNhks6qzqJDGHwwp7', '4dp6koFGapR3eELyTs7AZB5ZmwaHdyvU3vygj3yrzyLP',
                                  'Aqa8H5hmHe9MFY9sW6widbqEuaYv7q2KnRo25ApPhWhA', 'Fu6955kk7n7AZ8KLWtidAnfGjDaN78AByEJ34vvVV9vP',
                '6RKmvL7HBbZDAxX6JFCeLJ4apYaRwCwWBQR69qBSw4YG', 'JA6zU59PjKxYdTfWedyAK2DD9FHQbyu8coF68UM9je2c', 'EqhcpxYPJev46n6vDKgN7WFxv2iJC8CgDELiayaq19A4']

    async with httpx.AsyncClient() as client:
        tasks = [processWallet(wallet, client) for wallet in wallets]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # start_time = time.time()
    # asyncio.run(main())
    # print(f"Execution time: {time.time() - start_time} seconds")
    print(asyncio.run(getWalletTradeHistory("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"],
                                             httpx.AsyncClient())))
    #print(asyncio.run(getWalletAvgPrice("7tco85pE38UHUmaSNZRnsvcw2GXJv5TowP1tSw3GAL6M", "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", "buy", httpx.AsyncClient())))
