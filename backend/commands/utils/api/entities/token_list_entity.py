from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TokenListEntity:
    address: str
    decimals: int
    price: float
    lastTradeUnixTime: int
    liquidity: float
    logoURI: str
    mc: float
    name: str
    symbol: str
    v24hChangePercent: Optional[float]
    v24hUSD: float


@dataclass
class TokenListItems:
    """
    {
        "updateUnixTime": 1738352447,
        "updateTime": "2025-01-31T19:40:47.452Z",
        "tokens": [
            {
                "address": "So11111111111111111111111111111111111111112",
                "decimals": 9,
                "price": 231.22195015509826,
                "lastTradeUnixTime": 1738352401,
                "liquidity": 28114348733.32413,
                "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
                "mc": 112567896833.0687,
                "name": "Wrapped SOL",
                "symbol": "SOL",
                "v24hChangePercent": -22.519745178664678,
                "v24hUSD": 7672795665.463555
            },
        ]
    }
    """

    updateUnixTime: int
    updateTime: str
    tokens: List[TokenListEntity]
