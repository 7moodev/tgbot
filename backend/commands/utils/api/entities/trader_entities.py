from dataclasses import dataclass
from typing import List, Optional


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


@dataclass
class Quote:
    symbol: str
    decimals: int
    address: str
    amount: int
    type: str
    type_swap: str
    ui_amount: float
    price: Optional[float]
    nearest_price: float
    change_amount: int
    ui_change_amount: float


@dataclass
class Base:
    symbol: str
    decimals: int
    address: str
    amount: int
    type: str
    type_swap: str
    fee_info: Optional[float]
    ui_amount: float
    price: Optional[float]
    nearest_price: float
    change_amount: int
    ui_change_amount: float


@dataclass
class TraderSeekByTimeEntity:
    quote: Quote
    base: Base
    base_price: Optional[float]
    quote_price: Optional[float]
    tx_hash: str
    source: str
    block_unix_time: int
    tx_type: str
    address: str
    owner: str


@dataclass
class TraderSeekByTimeItems:
    """
    {
        "items": [
            {
            "quote": {
                "symbol": "USDC",
                "decimals": 6,
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "amount": 350351441,
                "type": "transfer",
                "type_swap": "from",
                "ui_amount": 350.351441,
                "price": null,
                "nearest_price": 0.99991594,
                "change_amount": -350351441,
                "ui_change_amount": -350.351441
            },
            "base": {
                "symbol": "SOL",
                "decimals": 9,
                "address": "So11111111111111111111111111111111111111112",
                "amount": 1610859019,
                "type": "transfer",
                "type_swap": "to",
                "fee_info": null,
                "ui_amount": 1.610859019,
                "price": null,
                "nearest_price": 216.65610374576917,
                "change_amount": 1610859019,
                "ui_change_amount": 1.610859019
            },
            "base_price": null,
            "quote_price": null,
            "tx_hash": "3bHiF6b9xmuAjanyLgvKbM2fnFSBo9FeY4rb67xrnGZWx24S6Yyroc8upiJgyUnG29p39jQqxfeRtZ5pTcT9hQJm",
            "source": "lifinity",
            "block_unix_time": 1731555934,
            "tx_type": "swap",
            "address": "DrRd8gYMJu9XGxLhwTCPdHNLXCKHsxJtMpbn62YqmwQe",
            "owner": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9"
            },
        ],
        "hasNext": true
    }
    """

    items: List[TraderSeekByTimeEntity]
    hasNext: bool
