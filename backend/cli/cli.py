import asyncio
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.holding_distribution import get_holding_distribution
from backend.commands.fresh_wallets import fresh_wallets

async def main():
    token = "9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump"
    print(token)
    limit = 50

    # # Fetch top holders' holdings
    # top_holders = await get_top_holders_holdings(token, limit)
    # print("Top Holders' Holdings:", top_holders)

    # # Fetch holding distribution
    # holding_distribution = await get_holding_distribution(token)
    # print("Holding Distribution:", holding_distribution)

    # # Fetch fresh wallets
    # fresh_wallets_data = await fresh_wallets(token, limit)
    # print("Fresh Wallets:", fresh_wallets_data)

if __name__ == "__main__":
    asyncio.run(main())
