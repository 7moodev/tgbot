from dataclasses import dataclass
from typing import List


@dataclass
class HistoryPriceEntity:
    address: str
    unixTime: int
    value: float


@dataclass
class HistoryPriceItems:
    """
    {
        "items": [
            {
                "address": "So11111111111111111111111111111111111111112",
                "unixTime": 1726700400,
                "value": 131.98719946668422
            },
            {
                "address": "So11111111111111111111111111111111111111112",
                "unixTime": 1726704000,
                "value": 135.06442939302468
            }
        ]
    },
    """

    items: List[HistoryPriceEntity]


@dataclass
class HistoricalPriceUnixEntity:
    """
    {
        "value": 128.09276765626564,
        "updateUnixTime": 1726675897,
        "priceChange24h": -4.924324221890145
    }
    """

    value: float
    updateUnixTime: int
    priceChange24h: float
