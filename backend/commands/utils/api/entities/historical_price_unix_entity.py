from dataclasses import dataclass


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
