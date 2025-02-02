from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class TokenOverviewEntity:
    """
    {
      "data": {
        "address": "So11111111111111111111111111111111111111112",
        "decimals": 9,
        "symbol": "SOL",
        "name": "Wrapped SOL",
        "extensions": {
          "coingeckoId": "solana",
          "serumV3Usdc": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
          "serumV3Usdt": "HWHvQhFmJB3NUcu1aihKmrKegfVxBEHzwVX6yZCKEsi1",
          "website": "https://solana.com/",
          "telegram": null,
          "twitter": "https://twitter.com/solana",
          "description": "Wrapped Solana ",
          "discord": "https://discordapp.com/invite/pquxPsq",
          "medium": "https://medium.com/solana-labs"
        },
        "logoURI": "https://img.fotofolio.xyz/?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsolana-labs%2Ftoken-list%2Fmain%2Fassets%2Fmainnet%2FSo11111111111111111111111111111111111111112%2Flogo.png",
        "liquidity": 7026510771.328585,
        "lastTradeUnixTime": 1726680782,
        "lastTradeHumanTime": "2024-09-18T17:33:02",
        "price": 128.88257145148586,
        "history30mPrice": 128.94328433830523,
        "priceChange30mPercent": -0.159524639847503,
        "history1hPrice": 128.11810104183903,
        "priceChange1hPercent": 0.4835280740819602,
        "history2hPrice": 127.37587477735319,
        "priceChange2hPercent": 1.0690511475458195,
        "history4hPrice": 129.4393197811086,
        "priceChange4hPercent": -0.5421318297548722,
        "history6hPrice": 129.40459359354182,
        "priceChange6hPercent": -0.5154419535367228,
        "history8hPrice": 130.34847971332593,
        "priceChange8hPercent": -1.2358346553114674,
        "history12hPrice": 131.0020403592915,
        "priceChange12hPercent": -1.7285626427832042,
        "history24hPrice": 133.1311635656234,
        "priceChange24hPercent": -3.3001856361757897,
        "uniqueWallet30m": 57965,
        "uniqueWalletHistory30m": 58256,
        "uniqueWallet30mChangePercent": -0.49951936281241416,
        "uniqueWallet1h": 82962,
        "uniqueWalletHistory1h": 78247,
        "uniqueWallet1hChangePercent": 6.025790126139021,
        "uniqueWallet2h": 113770,
        "uniqueWalletHistory2h": 132278,
        "uniqueWallet2hChangePercent": -13.991744658975794,
        "uniqueWallet4h": 188772,
        "uniqueWalletHistory4h": 147106,
        "uniqueWallet4hChangePercent": 28.323793726972387,
        "uniqueWallet8h": 274425,
        "uniqueWalletHistory8h": 278757,
        "uniqueWallet8hChangePercent": -1.554041692226563,
        "uniqueWallet24h": 729931,
        "uniqueWalletHistory24h": 528345,
        "uniqueWallet24hChangePercent": 38.154236341784255,
        "supply": 584763577.9554905,
        "mc": 75281052592.82196,
        "circulatingSupply": 584763577.9554905,
        "realMc": 75281052592.82196,
        "holder": 654340,
        "trade30m": 207770,
        "tradeHistory30m": 232071,
        "trade30mChangePercent": -10.47136436693943,
        "sell30m": 158199,
        "sellHistory30m": 174553,
        "sell30mChangePercent": -9.36907414939875,
        "buy30m": 49571,
        "buyHistory30m": 57518,
        "buy30mChangePercent": -13.81654438610522,
        "v30m": 176899.30659268858,
        "v30mUSD": 35155352.59832795,
        "vHistory30m": 132808.97974841399,
        "vHistory30mUSD": 42473437.5743586,
        "v30mChangePercent": 33.19830250017497,
        "vBuy30m": 99283.02631564619,
        "vBuy30mUSD": 20102318.860595156,
        "vBuyHistory30m": 67638.4612884733,
        "vBuyHistory30mUSD": 26812407.583997864,
        "vBuy30mChangePercent": 46.784868289967484,
        "vSell30m": 77616.28027704239,
        "vSell30mUSD": 15053033.73773279,
        "vSellHistory30m": 65170.51845994068,
        "vSellHistory30mUSD": 15661029.99036073,
        "vSell30mChangePercent": 19.097226953552514,
        "trade1h": 439841,
        "tradeHistory1h": 605277,
        "trade1hChangePercent": -27.332279270482772,
        "sell1h": 332752,
        "sellHistory1h": 405253,
        "sell1hChangePercent": -17.89030556220435,
        "buy1h": 107089,
        "buyHistory1h": 200024,
        "buy1hChangePercent": -46.46192456905172,
        "v1h": 309708.2863411133,
        "v1hUSD": 43136911.53837976,
        "vHistory1h": 524710.5797774522,
        "vHistory1hUSD": 21431757.36369426,
        "v1hChangePercent": -40.97540658081047,
        "vBuy1h": 166921.48760413667,
        "vBuy1hUSD": 30832829.31818354,
        "vBuyHistory1h": 277551.2080929021,
        "vBuyHistory1hUSD": 17584099.863855526,
        "vBuy1hChangePercent": -39.85921057556175,
        "vSell1h": 142786.79873697663,
        "vSell1hUSD": 12304082.220196217,
        "vSellHistory1h": 247159.37168455013,
        "vSellHistory1hUSD": 3847657.4998387345,
        "vSell1hChangePercent": -42.22885510519276,
        "trade2h": 1045118,
        "tradeHistory2h": 1155797,
        "trade2hChangePercent": -9.575989555259271,
        "sell2h": 738005,
        "sellHistory2h": 891529,
        "sell2hChangePercent": -17.220303545930644,
        "buy2h": 307113,
        "buyHistory2h": 264268,
        "buy2hChangePercent": 16.21270831125978,
        "v2h": 834418.8661186105,
        "v2hUSD": 15691541.686126484,
        "vHistory2h": 495189.80343672715,
        "vHistory2hUSD": 59150952.11645205,
        "v2hChangePercent": 68.50485618394369,
        "vBuy2h": 444472.69569706736,
        "vBuy2hUSD": 14566544.000268187,
        "vBuyHistory2h": 228523.56522462532,
        "vBuyHistory2hUSD": 46458917.37809091,
        "vBuy2hChangePercent": 94.4975325674517,
        "vSell2h": 389946.1704215431,
        "vSell2hUSD": 1124997.6858582962,
        "vSellHistory2h": 266666.23821210186,
        "vSellHistory2hUSD": 12692034.738361144,
        "vSell2hChangePercent": 46.23004885657346,
        "trade4h": 2200915,
        "tradeHistory4h": 1662229,
        "trade4hChangePercent": 32.40744807123447,
        "sell4h": 1629534,
        "sellHistory4h": 1239970,
        "sell4hChangePercent": 31.41721170673484,
        "buy4h": 571381,
        "buyHistory4h": 422259,
        "buy4hChangePercent": 35.31529227322567,
        "v4h": 1329608.669555223,
        "v4hUSD": 25855511.135367878,
        "vHistory4h": 660302.0733817923,
        "vHistory4hUSD": 59033726.51510045,
        "v4hChangePercent": 101.36369748856325,
        "vBuy4h": 672996.2609216414,
        "vBuy4hUSD": 11092666.897437705,
        "vBuyHistory4h": 348279.20300869434,
        "vBuyHistory4hUSD": 29084326.5769733,
        "vBuy4hChangePercent": 93.23469650435628,
        "vSell4h": 656612.4086335817,
        "vSell4hUSD": 14762844.237930173,
        "vSellHistory4h": 312022.8703730979,
        "vSellHistory4hUSD": 29949399.938127145,
        "vSell4hChangePercent": 110.43726950157362,
        "trade8h": 3863144,
        "tradeHistory8h": 3055770,
        "trade8hChangePercent": 26.42129479640156,
        "sell8h": 2869504,
        "sellHistory8h": 2216051,
        "sell8hChangePercent": 29.487272630458417,
        "buy8h": 993640,
        "buyHistory8h": 839719,
        "buy8hChangePercent": 18.33006041306675,
        "v8h": 1989910.7429370286,
        "v8hUSD": 145669294.83606875,
        "vHistory8h": 1988767.052141285,
        "vHistory8hUSD": 171858867.27861923,
        "v8hChangePercent": 0.05750752932638365,
        "vBuy8h": 1021275.4639303657,
        "vBuy8hUSD": 62216276.29504301,
        "vBuyHistory8h": 1013896.7152985546,
        "vBuyHistory8hUSD": 72820646.8791919,
        "vBuy8hChangePercent": 0.72776137060848,
        "vSell8h": 968635.2790066629,
        "vSell8hUSD": 83453018.54102576,
        "vSellHistory8h": 974870.3368427303,
        "vSellHistory8hUSD": 99038220.39942734,
        "vSell8hChangePercent": -0.6395781675192421,
        "trade24h": 12236742,
        "tradeHistory24h": 11564464,
        "trade24hChangePercent": 5.813308770730749,
        "sell24h": 9333890,
        "sellHistory24h": 8560524,
        "sell24hChangePercent": 9.03409651091452,
        "buy24h": 2902852,
        "buyHistory24h": 3003940,
        "buy24hChangePercent": -3.365180396412711,
        "v24h": 5986855.156929528,
        "v24hUSD": 747193016.9269896,
        "vHistory24h": 6417510.595781391,
        "vHistory24hUSD": 817861158.2096891,
        "v24hChangePercent": -6.710630741068936,
        "vBuy24h": 3025515.885840522,
        "vBuy24hUSD": 360668502.01211613,
        "vBuyHistory24h": 3188802.2403669828,
        "vBuyHistory24hUSD": 397383438.69322824,
        "vBuy24hChangePercent": -5.120617153971544,
        "vSell24h": 2961339.271089006,
        "vSell24hUSD": 386524514.9148734,
        "vSellHistory24h": 3228708.355414408,
        "vSellHistory24hUSD": 420477719.51646096,
        "vSell24hChangePercent": -8.280992114912914,
        "watch": null,
        "numberMarkets": 915424
      },
      "success": true
    }
    """

    address: str
    decimals: int
    symbol: str
    name: str
    extensions: dict
    logoURI: str
    liquidity: float
    lastTradeUnixTime: int
    lastTradeHumanTime: str
    price: float
    history30mPrice: float
    priceChange30mPercent: float
    history1hPrice: float
    priceChange1hPercent: float
    history2hPrice: float
    priceChange2hPercent: float
    history4hPrice: float
    priceChange4hPercent: float
    history6hPrice: float
    priceChange6hPercent: float
    history8hPrice: float
    priceChange8hPercent: float
    history12hPrice: float
    priceChange12hPercent: float
    history24hPrice: float
    priceChange24hPercent: float
    uniqueWallet30m: int
    uniqueWalletHistory30m: int
    uniqueWallet30mChangePercent: float
    uniqueWallet1h: int
    uniqueWalletHistory1h: int
    uniqueWallet1hChangePercent: float
    uniqueWallet2h: int
    uniqueWalletHistory2h: int
    uniqueWallet2hChangePercent: float
    uniqueWallet4h: int
    uniqueWalletHistory4h: int
    uniqueWallet4hChangePercent: float
    uniqueWallet8h: int
    uniqueWalletHistory8h: int
    uniqueWallet8hChangePercent: float
    uniqueWallet24h: int
    uniqueWalletHistory24h: int
    uniqueWallet24hChangePercent: float
    supply: float
    mc: float
    circulatingSupply: float
    realMc: float
    holder: int
    trade30m: int
    tradeHistory30m: int
    trade30mChangePercent: float
    sell30m: int
    sellHistory30m: int
    sell30mChangePercent: float
    buy30m: int
    buyHistory30m: int
    buy30mChangePercent: float
    v30m: float
    v30mUSD: float
    vHistory30m: float
    vHistory30mUSD: float
    v30mChangePercent: float
    vBuy30m: float
    vBuy30mUSD: float
    vBuyHistory30m: float
    vBuyHistory30mUSD: float
    vBuy30mChangePercent: float
    vSell30m: float
    vSell30mUSD: float
    vSellHistory30m: float
    vSellHistory30mUSD: float
    vSell30mChangePercent: float
    trade1h: int
    tradeHistory1h: int
    trade1hChangePercent: float
    sell1h: int
    sellHistory1h: int
    sell1hChangePercent: float
    buy1h: int
    buyHistory1h: int
    buy1hChangePercent: float
    v1h: float
    v1hUSD: float
    vHistory1h: float
    vHistory1hUSD: float
    v1hChangePercent: float
    vBuy1h: float
    vBuy1hUSD: float
    vBuyHistory1h: float
    vBuyHistory1hUSD: float
    vBuy1hChangePercent: float
    vSell1h: float
    vSell1hUSD: float
    vSellHistory1h: float
    vSellHistory1hUSD: float
    vSell1hChangePercent: float
    trade2h: int
    tradeHistory2h: int
    trade2hChangePercent: float
    sell2h: int
    sellHistory2h: int
    sell2hChangePercent: float
    buy2h: int
    buyHistory2h: int
    buy2hChangePercent: float
    v2h: float
    v2hUSD: float
    vHistory2h: float
    vHistory2hUSD: float
    v2hChangePercent: float
    vBuy2h: float
    vBuy2hUSD: float
    vBuyHistory2h: float
    vBuyHistory2hUSD: float
    vBuy2hChangePercent: float
    vSell2h: float
    vSell2hUSD: float
    vSellHistory2h: float
    vSellHistory2hUSD: float
    vSell2hChangePercent: float
    trade4h: int
    tradeHistory4h: int
    trade4hChangePercent: float
    sell4h: int
    sellHistory4h: int
    sell4hChangePercent: float
    buy4h: int
    buyHistory4h: int
    buy4hChangePercent: float
    v4h: float
    v4hUSD: float
    vHistory4h: float
    vHistory4hUSD: float
    v4hChangePercent: float
    vBuy4h: float
    vBuy4hUSD: float
    vBuyHistory4h: float
    vBuyHistory4hUSD: float
    vBuy4hChangePercent: float
    vSell4h: float
    vSell4hUSD: float
    vSellHistory4h: float
    vSellHistory4hUSD: float
    vSell4hChangePercent: float
    trade8h: int
    tradeHistory8h: int
    trade8hChangePercent: float
    sell8h: int
    sellHistory8h: int
    sell8hChangePercent: float
    buy8h: int
    buyHistory8h: int
    buy8hChangePercent: float
    v8h: float
    v8hUSD: float
    vHistory8h: float
    vHistory8hUSD: float
    v8hChangePercent: float
    vBuy8h: float
    vBuy8hUSD: float
    vBuyHistory8h: float
    vBuyHistory8hUSD: float
    vBuy8hChangePercent: float
    vSell8h: float
    vSell8hUSD: float
    vSellHistory8h: float
    vSellHistory8hUSD: float
    vSell8hChangePercent: float
    trade24h: int
    tradeHistory24h: int
    trade24hChangePercent: float
    sell24h: int
    sellHistory24h: int
    sell24hChangePercent: float
    buy24h: int
    buyHistory24h: int
    buy24hChangePercent: float
    v24h: float
    v24hUSD: float
    vHistory24h: float
    vHistory24hUSD: float
    v24hChangePercent: float
    vBuy24h: float
    vBuy24hUSD: float
    vBuyHistory24h: float
    vBuyHistory24hUSD: float
    vBuy24hChangePercent: float
    vSell24h: float
    vSell24hUSD: float
    vSellHistory24h: float
    vSellHistory24hUSD: float
    vSell24hChangePercent: float
    watch: Optional[None]
    numberMarkets: int
