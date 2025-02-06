from dataclasses import dataclass
from typing import List


@dataclass
class WalletPortfolioEntity:
    address: str
    name: str
    symbol: str
    decimals: int
    balance: str
    uiAmount: float
    chainId: str
    logoURI: str
    priceUsd: float
    valueUsd: float


@dataclass
class WalletPortfolioItems:
    """
    {
        "wallet": "0xf584f8728b874a6a5c7a8d4d387c9aae9172d621",
        "totalUsd": 177417911.42802328,
        "items": [
          {
            "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "name": "Tether USD",
            "symbol": "USDT",
            "decimals": 6,
            "balance": "72938605011215",
            "uiAmount": 72938605.011215,
            "chainId": "ethereum",
            "logoURI": "https://assets.coingecko.com/coins/images/325/small/Tether.png?1668148663",
            "priceUsd": 1.0000259715445037,
            "valueUsd": 72940499.33944109
          }
        ]
      }
    """

    wallet: str
    totalUsd: float
    items: List[WalletPortfolioEntity]
