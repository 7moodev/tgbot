from dataclasses import dataclass


@dataclass
class WalletTokenBalanceEntity:
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

    address: str
    name: str
    symbol: str
    decimals: int
    balance: int
    uiAmount: float
    chainId: str
    priceUsd: float
    valueUsd: float
