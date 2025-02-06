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
