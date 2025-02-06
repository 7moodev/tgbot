from dataclasses import dataclass
from typing import List


@dataclass
class TraderGainersLosersEntity:
    network: str
    address: str
    pnl: float
    trade_count: int
    volume: float


@dataclass
class TraderGainersLosersItems:
    """
    {
    "success": true,
    "data": {
        "items": [
        {
            "network": "solana",
            "address": "FciNKwZAvSzepKH1nFEGeejzbP4k87dJiP9BAzGt2Sm3",
            "pnl": 675542.1369220349,
            "trade_count": 74194,
            "volume": 1372626.717443506
        },
        {
            "network": "solana",
            "address": "Habp5bncMSsBC3vkChyebepym5dcTNRYeg2LVG464E96",
            "pnl": 175542.1369220349,
            "trade_count": 20,
            "volume": 1372626.717443506
        }
        ]
    }
    }
    """

    items: List[TraderGainersLosersEntity]
