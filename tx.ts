import { Connection, Keypair, LAMPORTS_PER_SOL, clusterApiUrl, PublicKey, Transaction, sendAndConfirmTransaction, SystemProgram, TransactionResponse, VersionedTransactionResponse, TokenAccountsFilter } from '@solana/web3.js';
import fetch from 'node-fetch';
if (!process.env.heliusrpc || !process.env.solscan || !process.env.solrpc) {
    throw new Error("Environment variables are not set");
}
const helius = process.env.heliusrpc;
const heliusConnection = new Connection(helius);
const solscanApi = process.env.solscan;
const quickNodeConnection = new Connection(process.env.solrpc);
const txCountHardLimit = 5000;
const maxTradesHardLimit = 100000000000;

interface Trade {
    activityType: string;
    transId: string;
    blockTime: number;
    token1: string;
    token1Decimals: number;
    token1Symbol: string;
    amount1: number;
    token2: string;
    token2Decimals: number;
    token2Symbol: string;
    side: number;
    amount2: number;
    time: string;
    avgPriceNative: number;
    avgPairNative: string;
    avgPriceUSD: number;
}
interface TokenPriceResponse {
    success: boolean;
    data: {
        date: number;
        price: number;
    }[];
}
interface History{
    trades: Trade[];
    holding: number;
    sold: number;
    avgBuy: number;
    avgSell: number;
    firstBuy:number;
    firstSell:number;
    lastSell:number;
}
interface ApiResponse {
    success: boolean;
    data: {
        routers: {
            amount1: number;
            amount2: number;
            token1: string;
            token2: string;
            token1_decimals: number;
            token2_decimals: number;
            avg_price_usd: number;
        };
        trans_id: string;
        block_time: number;
        activity_type: string;
        time: string;
    }[];
    metadata: {
        tokens: {
            [key: string]: {
                token_symbol: string;
            };
        };
    };
}
async function main(){
    let trades = await getTrades("713QQRd6NCcgLFiL4WFHcs84fAHrg1BLBSkiaUfP9ckF", "6gh8b2mqUrVb6Ew8Mwt89tNyN9keCDNstzT5cdp5pump");

    console.log(trades);
    //console.log(trades?.length);
    //console.log(await getTokenPrice("6gh8b2mqUrVb6Ew8Mwt89tNyN9keCDNstzT5cdp5pump"));
    // console.log(fromUnixTimeToYYYYMMDD(Date.now()/1000));
    // console.log(await getTokenPrice("So11111111111111111111111111111111111111112", "20240901"));
}
main();
function fromUnixTimeToYYYYMMDD(unixTime:number) {
    const date = new Date(unixTime * 1000);
    return date.getFullYear() +
           String(date.getMonth() + 1).padStart(2, '0') +
           String(date.getDate()).padStart(2, '0');
}
export async function getTokenPrice(tokenAddress:string, date:string="") {
    const requestOptions = {
        method: "get",
        headers: {"token": solscanApi }
    };
    let response;
    if (date!="") {
        response = await fetch(`https://pro-api.solscan.io/v2.0/token/price?address=${tokenAddress}&time[]=${date}`, requestOptions);
    } else {
        response = await fetch(`https://pro-api.solscan.io/v2.0/token/price?address=${tokenAddress}`, requestOptions);
    }
    const data = await response.json() as TokenPriceResponse;
    if (data.success) {
        if (data.data.length > 0) {
            return data.data[0].price;
        }  
    }
    return 0;
}
export async function getTrades(address: string, token: string="", maxTrades: number=maxTradesHardLimit) {
    const requestOptions = {
        method: "get",
        headers: {
            "token": process.env.solscan || ""
        }
    };
    let currentPrice = await getTokenPrice(token);
    let purchased = 0;
    let sold = 0;
    let totalCost = 0;
    let avgBuyPrice = 0;
    let avgSellPrice = 0;
    let lowestBuyPrice = Number.MAX_VALUE;
    let highestSellPrice = Number.MIN_VALUE;
    let currentPage = 1;
    let response;
    let trades: Trade[] = [];
    try {
        while (trades.length < maxTrades) {
            console.log("currentPage: " + currentPage);
            console.log("trades.length: " + trades.length);
            if (token == "") {
                response = await fetch(`https://pro-api.solscan.io/v2.0/account/defi/activities?address=${address}&page=${currentPage}&page_size=40&sort_by=block_time&sort_order=desc`, requestOptions);
            } else {
                response = await fetch(`https://pro-api.solscan.io/v2.0/account/defi/activities?address=${address}&token=${token}&page=${currentPage}&page_size=40&sort_by=block_time&sort_order=desc`, requestOptions);
            }
            const data = await response.json() as ApiResponse;
            const tokens = data.metadata.tokens;
            if (!data.data || data.data.length === 0) {
                break;
            }
            data.data.map(async (data) => {
                let amount1 = data.routers.amount1/10**data.routers.token1_decimals;
                let amount2 = data.routers.amount2/10**data.routers.token2_decimals;
                let token1Symbol = tokens[data.routers.token1].token_symbol;
                let token2Symbol = tokens[data.routers.token2].token_symbol;
                let side: number = token === data.routers.token1 ? -1 : 1;
                let token1Price=1;
                let token2Price=1;
                if (!(token1Symbol == "USDC" || token1Symbol == "USDT" || token1Symbol == "USDCe")) {
                    token1Price = await getTokenPrice(data.routers.token1, fromUnixTimeToYYYYMMDD(data.block_time));
                }
                if (!(token2Symbol == "USDC" || token2Symbol == "USDT" || token2Symbol == "USDCe")) {
                    token2Price = await getTokenPrice(data.routers.token2, fromUnixTimeToYYYYMMDD(data.block_time));
                } 
                totalCost += side == 1 ? amount1*token1Price : 0;
                totalCost -= side == -1 ? amount2*token2Price : 0;
                purchased += side == 1 ? amount1 : 0;
                sold += side == -1 ? amount2 : 0;
                lowestBuyPrice = Math.min(lowestBuyPrice, side == 1 ? token1Price : lowestBuyPrice);
                highestSellPrice = Math.max(highestSellPrice, side == -1 ? token2Price : highestSellPrice);
                
                if (data.activity_type === "ACTIVITY_AGG_TOKEN_SWAP" || data.activity_type === "ACTIVITY_TOKEN_SWAP") {
                    //console.log(data);
                    
                    trades.push({
                        activityType: data.activity_type,
                        transId: data.trans_id,
                        blockTime: data.block_time,
                        token1: data.routers.token1,
                        token1Decimals: data.routers.token1_decimals,
                        token1Symbol: token1Symbol,
                        amount1: amount1,
                        token2: data.routers.token2,
                        token2Decimals: data.routers.token2_decimals,
                        token2Symbol: token2Symbol,
                        side: side,
                        amount2: amount2,
                        time: data.time,
                        avgPriceNative: side == 1 ? amount1/amount2 : amount2/amount1,
                        avgPairNative: token1Symbol+"/"+token2Symbol,
                        avgPriceUSD: (side == 1 && token1Price > 0 && token2Price > 0) ? token1Price/token2Price : (side == -1 && token1Price > 0 && token2Price > 0) ? token2Price/token1Price : 0,
                    });
                    //console.log(trades[trades.length-1]);
              
                }
                //console.log(trades);
            });
            console.log(trades);
            currentPage++;
            
            if (trades.length > maxTrades) {
             

                console.log("Trades length is greater than maxTrades, slicing trades");
                trades = trades.slice(0, maxTrades);
            }
            

        }

        // console.log("lowestBuyPrice: " + lowestBuyPrice);
        // console.log("highestSellPrice: " + highestSellPrice);
        // console.log("purchased: " + purchased);
        // console.log("sold: " + sold);
        // console.log("totalCost: " + totalCost);
        console.log(trades);
        return trades;
    } catch(e) {
        console.log(e);
        return []; // Return empty array instead of undefined on error
    }
}

