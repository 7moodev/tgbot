import { Connection, Keypair, LAMPORTS_PER_SOL, clusterApiUrl, PublicKey, Transaction, sendAndConfirmTransaction, SystemProgram, TransactionResponse, VersionedTransactionResponse, TokenAccountsFilter } from '@solana/web3.js';
import * as bs58 from 'bs58';
import { getTrades } from './tx';
import fetch from 'node-fetch';
import fs from 'fs';
if (!process.env.heliusrpc || !process.env.solscan || !process.env.solrpc) {
    throw new Error("Environment variables are not set");
}
const helius = process.env.heliusrpc;
const heliusConnection = new Connection(helius);
const solscanApi = process.env.solscan;
const quickNodeConnection = new Connection(process.env.solrpc);
const txCountHardLimit = 5000;

interface TokenMeta {
    success: boolean;
    data: {
        holder: number;
        decimals: number;
        address: string;
        name: string;
        symbol: string;
        icon: string;
        creator: string;
        create_tx: string;
        created_time: number;
        first_mint_tx: string;
        first_mint_time: number;
        mint_authority: string | null;
        freeze_authority: string | null;
        supply: string;
        price: number;
        volume_24h: number;
        market_cap: number;
        market_cap_rank: number;
        price_change_24h: number;
    };
}

interface Trade{
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

async function getConnection() {
    if (Date.now() % 2 == 0) {
        return quickNodeConnection;
    }
    return heliusConnection;
}
async function main() {
    //console.log(solscanApi);
    //await findHolders("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263");
   //console.log( await getTokenLargestAccounts("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"));
   // console.log(await getTopTokenHolders("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump",10));
   // await getWalletAge(quickNodeConnection, "7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs");
    //console.log(await getTokenHolderCount("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump"));
    //console.log(await getWalletAgeInHours("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"))
   // console.log(await getTopTokenHolders("3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",5));
    //console.log(await getSignatures("5gUbEaiscJHhekG2vafDxts8R6CRpfp8WV5JAGuRpump"), 100000000);
    //console.log(await getTokenMaxSupply("3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"));
    console.log(await getTrades("7BB5A9XagbYTZkWXeusmeVgdBwa18P8UTGHQcVhiygs"));
  // console.log(await getTokenPrice("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"));
   //console.log(fromUnixTimeToYYYYMMDD(1733256784));
}
async function getSignatures(address:string, limit:number = txCountHardLimit) {
    console.log(`Fetching signatures for address: ${address}`);
    let signatures: any[] = [];
    let connection = await getConnection();
    let initialSignatures = await connection.getSignaturesForAddress(new PublicKey(address));
    signatures.push(...initialSignatures);
    while (initialSignatures.length == 1000 && signatures.length < txCountHardLimit) {
        
        const options = {
            before: initialSignatures[initialSignatures.length - 1].signature,
        };
        initialSignatures = await connection.getSignaturesForAddress(new PublicKey(address), options);
        signatures.push(...initialSignatures);
    }
    return signatures;
}
async function getWalletAgeInHours(address:string) {
    console.log("Fetching wallet age for address:", address);
    const unixTimeInSeconds = Math.round(Date.now() / 1000);
    const connection = await getConnection();
    let signatures = await getSignatures(address);
    if (signatures.length == txCountHardLimit) {
        return 99999;
    }
    const lastSignature = signatures[signatures.length - 1];
    let transactionAge = unixTimeInSeconds - (lastSignature.blockTime ?? unixTimeInSeconds);
    return Math.round(transactionAge/3600);
}
async function unixTimeToDate(unixTime:number) {
    return new Date(unixTime * 1000).toLocaleString();
}
async function fromHourstoReadable(hours:number) {
    if (hours == 99999) {
        return "Unknown: Frequent Transactions";
    }
    if (hours < 24) {
        return `${Math.round(hours)} Hours`;
    }
    else if (hours < 720) {
        return `${Math.round(hours / 24)} Days`;
    }
    else if (hours < 8760) {
        return `${Math.round(hours / 720)} Months`;
    }
    else {
        return `${Math.round(hours / 8760)} Years`;
    }
}
interface TokenHolder {
    address: string;
    rank: number;
    amount: number;
    decimals: number;

}
interface ApiTokenHolder {
    address: string;
    rank: number;
    amount: number;
    decimals: number;
}
interface TokenResponse {
    success: boolean;
    data: {
        total: number;
        items: ApiTokenHolder[];
    };
}
async function getTopTokenHolders(tokenAddress: string, maxHolders: number, from:number = 0, to:number = 999999999999999) { //solscan
    const startTime = performance.now();
    const requestOptions = {
        method: "get",
        headers: {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzA0NzIxMTkyOTQsImVtYWlsIjoiYmF5cmFtLndpbHNvbjA0QGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTczMDQ3MjExOX0.yFuLfml12MylfJ4wNKNNBkUPpL68x7YyZBe5T0Tp5nM"
        }
    };
    let allHolders: TokenHolder[] = [];
    let currentPage = 1;
    try {
        while (allHolders.length < maxHolders) {
            let PAGE_SIZE = 40;
            if (maxHolders-allHolders.length < PAGE_SIZE) {
                PAGE_SIZE = Math.min(Math.ceil(maxHolders/10)*10, 40);
            }
            const response = await fetch(
                `https://pro-api.solscan.io/v2.0/token/holders?address=${tokenAddress}&page=${currentPage}&page_size=${PAGE_SIZE}&from_amount=${from}&to_amount=${to}`,
                requestOptions
            );
            const data = await response.json() as TokenResponse;
            if (!data.success || !data.data.items.length) {
                break; // No more holders to fetch
            }
            // Directly map and append to allHolders
            allHolders = [
                ...allHolders,
                ...data.data.items.map(item => ({
                    address: item.address,
                    rank: item.rank,
                    amount: item.amount / Math.pow(10, item.decimals),
                    decimals: item.decimals,
                }))
            ];
            currentPage++;
            // If we've fetched more than we need, trim the excess
            if (allHolders.length > maxHolders) {
                allHolders = allHolders.slice(0, maxHolders);
            }
            const connection = await getConnection();
            const tokenMaxSupply = await getTokenMaxSupply(tokenAddress);
            const adjustedHolders = await Promise.all(allHolders.map(async (holder) => ({
                ...holder,
                walletAge: await fromHourstoReadable(await getWalletAgeInHours(holder.address)),
                solHolding: (await connection.getBalance(new PublicKey(holder.address)))/LAMPORTS_PER_SOL,
                holdingInPercent: holder.amount / tokenMaxSupply * 100
            })));
            allHolders = adjustedHolders;
        }
        const endTime = performance.now();
        console.log(`Execution time: ${endTime - startTime} milliseconds`);
        console.log(`Total holders fetched: ${allHolders.length}`);
        return allHolders;
    } catch (error) {
        const endTime = performance.now();
        console.log(`Execution time (with error): ${endTime - startTime} milliseconds`);
        console.error("Error fetching holders:", error);
        return [];
    }
}
async function getTokenHolderCount(tokenAddress: string) {
    const requestOptions = {
        method: "get",
        headers: {"token": solscanApi }
    };
    try {
        const response = await fetch(`https://pro-api.solscan.io/v2.0/token/meta?address=${tokenAddress}`, requestOptions);
        const meta = await response.json() as TokenMeta;
        if (meta.success) {
            return meta.data.holder;
        }
    } catch (error) {
        console.error(error);
        return 0;
    }
}
async function getTokenMaxSupply(tokenAddress:string) {
    const connection = await getConnection();
    const tokenInfo = await connection.getTokenSupply(new PublicKey(tokenAddress));
    return +(tokenInfo.value.uiAmountString ?? "0");
}
function fromUnixTimeToYYYYMMDD(unixTime:number) {
    const date = new Date(unixTime * 1000);
    return date.getFullYear() +
           String(date.getMonth() + 1).padStart(2, '0') +
           String(date.getDate()).padStart(2, '0');
}



const findAllHolders = async (mint:string) => {
    /**
     * Find all holders of a token using Helius
     */
    let page = 1;
    let allOwners = new Set();
    while (true) {
      const response = await fetch(helius, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          method: "getTokenAccounts",
          id: "helius-test",
          params: {
            page: page,
            limit: 1000,
            displayOptions: {},
            mint: mint,
          },
        }),
      });
          // Check if any error in the response
        if (!response.ok) {
          console.log(
            `Error: ${response.status}, ${response.statusText}`
          );
          break;
        }
  
      interface TokenResponse {
          result: {
              token_accounts: Array<{
                  owner: string;
              }>;
          };
      }
  
      const data = await response.json() as TokenResponse;
  
      if (!data.result || data.result.token_accounts.length === 0) {
        console.log(`No more results. Total pages: ${page - 1}`);
  
        break;
      }
      console.log(`Processing results from page ${page}`);
      data.result.token_accounts.forEach((account:any) =>
        allOwners.add(account.owner)
      );
      page++;
    }
    fs.writeFileSync(
      "output.json",
      JSON.stringify(Array.from(allOwners), null, 2)
    );
    console.log(`Total holders: ${allOwners.size}`);
  };
main(); 