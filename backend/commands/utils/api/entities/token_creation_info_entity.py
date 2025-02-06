from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenCreationInfoEntity:
    """
    {
        "txHash": "3cW2HpkUs5Hg2FBMa52iJoSMUf8MNkkzkRcGuBs1JEesQ1pnsvNwCbTmZfeJf8hTi9NSHh1Tqx6Rz5Wrr7ePDEps",
        "slot": 223012712,
        "tokenAddress": "D7rcV8SPxbv94s3kJETkrfMrWqHFs6qrmtbiu6saaany",
        "decimals": 5,
        "owner": "JEFL3KwPQeughdrQAjLo9o75qh15nYbFJ2ZDrb695qsZ",
        "blockUnixTime": 1697044029,
        "blockHumanTime": "2023-10-11T17:07:09.000Z"
    }
    """

    txHash: str
    slot: int
    tokenAddress: str
    decimals: int
    owner: str
    blockUnixTime: int
    blockHumanTime: datetime
