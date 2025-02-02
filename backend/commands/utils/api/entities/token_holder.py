from dataclasses import dataclass
from typing import List


@dataclass
class TokenHolderEntity:
    amount: str
    decimals: int
    mint: str
    owner: str
    token_account: str
    ui_amount: int


@dataclass
class TokenHolderItems:
    """
    {
        "items": [
        {
            "amount": "100000000000",
            "decimals": 9,
            "mint": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
            "owner": "6Zk9e3nfXdYLXHYu5NvDiPHGMcjujVBv6gWRr7ckSdhP",
            "token_account": "HdmGPmTkBgsiJcyVDgiGkYdTZr4h5XmpjYoUjU2rapf4",
            "ui_amount": 100
        },
        {
            "amount": "90000000000",
            "decimals": 9,
            "mint": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
            "owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
            "token_account": "EauuZAnB7CcnCrwvCMcnb2Rjk12Ecs13ycAZQBb5tLYM",
            "ui_amount": 90
        }
        ]
    }
    """

    items: List[TokenHolderEntity]
