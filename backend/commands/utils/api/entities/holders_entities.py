from ast import List
from dataclasses import dataclass
from typing import Any

from backend.commands.utils.api.entities.token_entities import TokenOverviewEntityFocus


@dataclass
class TopHoldingEntity:
    """
    {
        "address": "12ifMz54Sq4Ab4RiPezsbDYkY2fo5L3VTabfJJ2ppump",
        "decimals": 6,
        "balance": 20568096238965,
        "uiAmount": 20568096.238965,
        "chainId": "solana",
        "name": "PAIN",
        "symbol": "PAIN",
        "icon": "https://ipfs.io/ipfs/QmQVqtGhNjJEdcbFXMZsiyr2w48YCTmXwMK76wXyjQQuMH",
        "logoURI": "https://ipfs.io/ipfs/QmQVqtGhNjJEdcbFXMZsiyr2w48YCTmXwMK76wXyjQQuMH",
        "priceUsd": 0.0002848390208054348,
        "valueUsd": 5858.596392538737
    }
    """

    address: str
    decimals: int
    balance: int
    uiAmount: float
    chainId: str
    name: str
    symbol: str
    icon: str
    logoURI: str
    priceUsd: float
    valueUsd: float


@dataclass
class TopHoldersOfTokenEntity:
    """
    {
        "count": 2,
        "wallet": "71fMKsyav7usgjmkbcegAU63uhwLQwipyyLDbJ6Lcijp",
        "amount": 20568096.238965,
        "share_in_percent": 2.057,
        "net_worth": 25188.115259487266,
        "net_worth_excluding": 19329.51886694853,
        "first_top_holding": {
            "address": "98mb39tPFKQJ4Bif8iVg9mYb9wsfPZgpgN1sxoVTpump",
            "decimals": 6,
            "balance": 1927787500554,
            "uiAmount": 1927787.500554,
            "chainId": "solana",
            "name": "Large Language Model",
            "symbol": "LLM",
            "icon": "https://ipfs.io/ipfs/QmQmQUoTpBBcgnA5Bx5KpmgNLqLMuRRzvrUf3h85xUqo7W",
            "logoURI": "https://ipfs.io/ipfs/QmQmQUoTpBBcgnA5Bx5KpmgNLqLMuRRzvrUf3h85xUqo7W",
            "priceUsd": 0.003645575280959077,
            "valueUsd": 7027.894458961546
        },
        "second_top_holding": {
            "address": "12ifMz54Sq4Ab4RiPezsbDYkY2fo5L3VTabfJJ2ppump",
            "decimals": 6,
            "balance": 20568096238965,
            "uiAmount": 20568096.238965,
            "chainId": "solana",
            "name": "PAIN",
            "symbol": "PAIN",
            "icon": "https://ipfs.io/ipfs/QmQVqtGhNjJEdcbFXMZsiyr2w48YCTmXwMK76wXyjQQuMH",
            "logoURI": "https://ipfs.io/ipfs/QmQVqtGhNjJEdcbFXMZsiyr2w48YCTmXwMK76wXyjQQuMH",
            "priceUsd": 0.0002848390208054348,
            "valueUsd": 5858.596392538737
        },
        "third_top_holding": {
            "address": "So11111111111111111111111111111111111111111",
            "decimals": 9,
            "balance": 20926983410,
            "uiAmount": 20.92698341,
            "chainId": "solana",
            "name": "SOL",
            "symbol": "SOL",
            "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            "priceUsd": 196.18839323267412,
            "valueUsd": 4105.631250414727
        }
    }
    """

    count: int
    wallet: str
    amount: float
    share_in_percent: float
    net_worth: float
    net_worth_excluding: float
    first_top_holding: TopHoldingEntity
    second_top_holding: TopHoldingEntity
    third_top_holding: TopHoldingEntity


@dataclass
class TopHolderEntity:
    token_info: TokenOverviewEntityFocus
    items: List[TopHoldersOfTokenEntity]
