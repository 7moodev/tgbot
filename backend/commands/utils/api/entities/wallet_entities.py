from dataclasses import dataclass
from typing import List


@dataclass
class WalletEntity:
    address: str
    name: str
    symbol: str
    decimals: int
    balance: str
    chainId: str


@dataclass
class WalletBalance:
    uiAmount: float
    priceUsd: float
    valueUsd: float


@dataclass
class WalletPortfolioEntity(WalletEntity, WalletBalance):
    logoURI: str


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


@dataclass
class WalletTokenBalanceEntity(WalletEntity, WalletBalance):
    """
    {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "name": "Tether USD",
        "symbol": "USDT",
        "decimals": 6,
        "balance": 94149341656019,
        "uiAmount": 94149341.656019,
        "chainId": "eth-mainnet",
        "priceUsd": 0.9999915198446391,
        "valueUsd": 94149341656019.2
    }
    """

    pass
