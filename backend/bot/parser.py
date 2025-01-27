from ctypes import memset

from aiohttp.http import WebSocketReader
from .tg_format_test import send_message
from ..commands.top_holders_holdings import get_top_holders_holdings
from ..commands.holding_distribution import get_holding_distribution 
from ..commands.fresh_wallets import fresh_wallets
from ..commands.fresh_wallets_v2 import fresh_wallets_v2
from ..commands.noteworthy_addresses import get_noteworthy_addresses
import time
import asyncio
import json
import ast
import re, os

running = 1 # switch to change between jsons and actual data for testing/parsing

'''
TODO: Use splitfunction and send messages in chunks if exeeds 4096 characters
'''
MAX_MESSAGE_LENGTH = 4096
def split_message(text):
    return [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]

def format_number(amount, with_dollar_sign=True):
    if with_dollar_sign:
        amount = round(amount)
    """
    Converts a number to a readable money format.
    
    :param amount: The number to be formatted.
    :param with_dollar_sign: Boolean that determines whether to include the dollar sign.
    :return: A formatted string with the appropriate money notation.
    """
    if with_dollar_sign:
        prefix = "$"
    else:
        prefix = ""

    # Define thresholds for 'k', 'm', and 'b' suffixes
    if amount >= 1_000_000:
        formatted_amount = f"{amount / 1_000_000:.1f}m"  # Millions (1m = 1,000,000)
    elif amount >= 1_000:
        formatted_amount = f"{amount / 1_000:.1f}k"  # Thousands (1k = 1,000)
    else:
        formatted_amount = str(amount)  # No suffix for smaller amounts

    # Remove the ".0" from whole numbers
    if formatted_amount.endswith(".0"):
        formatted_amount = formatted_amount[:-2]

    return escape_markdown(f"{prefix}{formatted_amount}")

def escape_markdown(text):
    # List of characters that need to be escaped in Markdown
    special_chars = r'\`_{}[]()#+-.!|<>'
    # Use a regular expression to replace each special character with a backslash and the character
    return re.sub(r'([{}])'.format(re.escape(special_chars)), r'\\\1', text)

def check_noteworthy(top_holders, cutoff=50_000):
#    print(type(top_holders))  # Debugging: Check the type of top_holders
#    print(top_holders)        # Debugging: Print the entire top_holders list
#    print(len(top_holders))   # Debugging: Print the length of top_holders

    noteworthy = []
    for holder in top_holders:
        try:
            # Check if 'net_worth' exists and is a valid number
            if 'net_worth_excluding' in holder and isinstance(holder['net_worth_excluding'], (int, float)):
                if holder['net_worth_excluding'] > cutoff:
                    noteworthy.append(holder)
            else:
                print(f"Skipping holder due to missing or invalid 'net_worth': {holder}")
        except Exception as e:
            print(f"Error processing holder: {holder}. Error: {e}")

    return noteworthy
    
def generate_socials_message(token_info, token):
    # Start with the base message format
    message = "├"
    chart_link = f"[📊*CHART*](https://dexscreener.com/solana/{token})"


    # Check if extensions exist and is not None
    if token_info.get('extensions'):
        extensions = token_info['extensions']
        
        # Check for 'website' in extensions and add the link if it exists
        if extensions.get('website'):
            website_link = f"──[*WEB*]({extensions['website']})"
        else:
            website_link = ""  # Leave it empty if 'website' doesn't exist
        message += f"{website_link}"
        # Add the chart link for DexScreener
                
        # Add the website and chart link to the message
        if extensions.get('twitter'):
            message += f"──[*X*]({extensions.get('twitter')})"

        message += f"──{chart_link}\n"
        
    else:
        # If extensions is None or doesn't exist, just include the chart link
        message += chart_link

    return message 

async def top_holders_holdings_parsed(token, limit):
    if running:
        data = await get_top_holders_holdings(token, limit)
        token_info =  data['token_info']
        top_holders= data ['items']

    else:
        print ('parsing from json')

        data = json.load(open("backend/commands/outputs/top_holders_holdings.json", 'r'))
        
        token_info =  data['token_info']
        top_holders= data ['items']



    #print(token_info)
      # Token information part= 


    message = f"*Token Info*: {token_info['symbol']} \\({token_info['name']}\\)\n"
    message += generate_socials_message(token_info, token)
    message += f"├──💰 MC: {format_number(token_info['market_cap'])}\n"
    message += f"├──🫗 Liquidity: {format_number(token_info['liquidity'])}\n"
    message += f"├──👥Total Holder: {token_info['holder']:,}\n\n"
    message += f"*CA*: `{token}`\n\n"
    

    noteworthy = check_noteworthy(top_holders)  
    message += f"* 💰 There are {len(noteworthy)}/ {len(top_holders)} noteworthy top holders:*\n\n"


    message_parts = []
    current_message = message


    # Top holders part
    for holder in noteworthy:
        #print (holder)
        wallet = holder['wallet']
        short_wallet = escape_markdown( shorten_address(wallet) ) 
        addy = f"(https://solscan.io/account/{wallet})"
        dollar_token_share = holder['net_worth']- holder['net_worth_excluding']
        whale = ""
        if dollar_token_share > 100_000: 
            whale = "🐳 "
        elif dollar_token_share > 10_000: 
            whale = "🦈 "
        elif dollar_token_share > 5_000: 
            whale = "🐬 "
        elif dollar_token_share > 1000: 
            whale = "🐟 "
        elif dollar_token_share > 100: 
            whale = "🦐 "
        elif dollar_token_share > 10: 
            whale = "🫧 "



        try:
            if "error" in holder:
                h_info += f"{whale}\\# {holder['count']}\\-\\({addy}\\)\\(💰 NW\\_Excl: $1M+\\) 🏦LP/Bot \\|\n"
                continue

            #addy = f"[{shorten_address(wallet)}](https://solscan.io/account/{wallet})"
            h_info = f"[{whale}\\#{holder['count']}\\({format_number(dollar_token_share)}\\)]{addy}  \\| "
            top1 = holder['first_top_holding']
            top2 = holder['second_top_holding']
            top3 = holder['third_top_holding']
            top_list = [top1, top2, top3]
            processed = []
            for top in top_list:
                if top['symbol'] != token_info['symbol']:
                    if top not in processed:
                        processed.append(top)
                        symbol =escape_markdown(top['symbol'])
                        symbol = f"{symbol}" 
                        h_info += (f"`{symbol}`: {format_number(top['valueUsd'])}, ")
            
            h_info = h_info[:-2] + "\n" # Remove the trailing comma and add a newline
#
                    

#            if top1['symbol'] != token_info['symbol']:
#                symbol =escape_markdown(top1['symbol'])
#                symbol = f"{symbol}"#(https://dexscreener.com/solana/{top1['address']})"
#                h_info += (f"`{symbol}`: {format_number(top1['valueUsd'])}, ")
#                top_list = [x for x in top_list if x != top1]
#                
#            if top2['symbol'] != token_info['symbol']:
#                symbol =escape_markdown(top2['symbol'])
#                symbol = f"{symbol}"#](https://dexscreener.com/solana/{top2['address']})"
#                h_info += (f"`{symbol}`: {format_number(top2['valueUsd'])}, ")
#            if top3['symbol'] != token_info['symbol']:
#                symbol =escape_markdown(top3['symbol'])
#                symbol = f"{symbol}"#](https://dexscreener.com/solana/{top3['address']})"
#                h_info += (f"`{symbol}`: {format_number(top3['valueUsd'])} \n")


            if len(current_message) + len(h_info) > 4096:
                # If it exceeds, save the current message and start a new one
                message_parts.append(current_message)
                current_message = h_info  # Start a new message with the current holder
            else:
                # Otherwise, append the holder's message to the current message
                current_message += h_info


        except Exception as e:
            print(f" holder: {holder}")
            print(f"Error processing holder: {e}")
        h_info += "\n"

    if current_message:
        message_parts.append(current_message)

    # Print and return all message parts
    for part in message_parts:
        print(part)
    return message_parts

async def holder_distribution_parsed(token):
    
    '''
    TODO: Add Error handling
    '''
    if running:
        data = await get_holding_distribution(token)
    else:
        print ('parsing from json')

        data = [{'0-500': 72.0, '500-1000': 2.0, '1000-5000': 6.0, '5000-25000': 2.0, '25000+': 18.0}, {'holder_count': 7199, 'retrieved_holders': 50, 'Symbol': 'Mizuki', 'Name': 'Mizuki'}, {'symbol': 'Mizuki', 'name': 'Mizuki', 'logo_url': 'https://ipfs.io/ipfs/Qmdtq5b4Z5JouWWothvSXydP3Rz8WyqTKtQVXhh5LiZrrR', 'liquidity': 828098.4949007538, 'market_cap': 18011571.94138404}]
    token_info = data[2]
    #logo_url = token_info['logo_url']
    # Distribution
    data_pc = data[0]
    data_meta = data[1]
    distribution = [
        ("🫧", "0-500", data_pc['0-500']),
        ("🦐", "500-1000", data_pc['500-1000']),
        ("🐟", "1000-5000", data_pc['1000-5000']),
        ("🐬", "5000-25000", data_pc['5000-25000']),
        ("🦈", "25000+", data_pc['25000+'])
    ]
    
    # Create the bar visualization
    bars = []
    for emoji, range_str, percentage in distribution:
        bar_length = int(percentage / 10) if percentage > 0 else 0
        bar = "🟩" * bar_length
        bars.append(escape_markdown(f"{emoji} |{bar} {percentage}%"))

    # Convert percentages to holder counts (assuming all holders are represented by '25000+')
    total_holders = data_meta['holder_count']
    holder_counts = {
        "🫧 holding (0-500)": int(total_holders * data_pc['0-500'] / 100),
        "🦐 holding (500-1000)": int(total_holders * data_pc['500-1000'] / 100),
        "🐟 holding (1000-5000)": int(total_holders * data_pc['1000-5000'] / 100),
        "🐬 holding (5000-25000)": int(total_holders * data_pc['5000-25000'] / 100),
        "🦈 holding (25000+)": int(total_holders * data_pc['25000+'] / 100)
            }

    info  =f"\n*Token Info*: {token_info['symbol']} \\({token_info['name']}\\)\n"
    info += f"├── MC: {format_number(token_info['market_cap'])}\n"
    info += f"├── Liquidity: {format_number(token_info['liquidity'])}\n"
    info += f"\n*Total Holders*: {total_holders:,}\n"

    # Generate the Markdown message
    markdown = """📊 Holding Distributions for ${symbol}:
\\- by @munki\\_bot🦧{info}
{bars}\n""".format(symbol=data_meta['Symbol'], bars='\n'.join(bars), info=info)

    markdown += "\n"
    for emoji, count in holder_counts.items():
        markdown += escape_markdown(f"{emoji}:  {count}\n")

   
    return markdown, logo_url


def shorten_address(address: str, length: int = 2) -> str:
    """
    Shorten the address to the given length.
    """
    return f"{address[:length]}.{address[-length:]}"
# Convert to the readable format
async def fresh_wallets_parsed(token, limit):

    if running:
        data = await fresh_wallets(token, limit)
        token_info = data ['token_info'] 
        wallet_ages = data ['items']
        print(wallet_ages)

    
    else:
        print ('parsing from json')
        data = json.load(open("backend/commands/outputs/fresh_wallets.json", 'r'))
        token_info = data ['token_info'] 
        wallet_ages = data ['items']

    token_symbol = token_info['symbol']
    token_name = token_info['name']
    market_cap = format_number(token_info['market_cap'])
    liquidity = format_number(token_info['liquidity'])
    holder = format_number(token_info['holder'], with_dollar_sign=False)
    message_parts = [
        f"*Token*: {token_symbol} \\({token_name}\\)\n",
        f"├──💰 MC: {market_cap}\n",
        f"├──💦 Liquidity: {liquidity}\n",
        f"├──👥 Holders count: {holder}\n",
        f"Fresh Wallets Detector\n\n",
        escape_markdown(f"🔴: <1 Week\n"),
        escape_markdown(f"🟠: <1 Month\n"),
        escape_markdown(f"🟡: <3 Months\n"),
        escape_markdown(f"🟢: >3 Months\n"),
        escape_markdown(f"🔵: LP/Bot \n\n"),
        escape_markdown(f"Ordered by holding --------->\n\n"),
    ]
    
    # Precompute current time
    current_time = int(time.time())
    count=0

    for wallet in wallet_ages:
        if count == 50:
            break
        if count %10 == 0:
            message_parts.append("\n")
        if 'error' in wallet:
            print (f"Error processing wallet: {wallet}")
            continue
        if wallet.get('age') is not None:
            wallet_age_unix = wallet['age']
            if wallet_age_unix == 0:   
                message_parts.append(f"🔵 ")#(https://solscan.io/account/{wallet['wallet']})")
                count+=1
                continue
            # Calculate age in days only
            age_seconds = current_time - wallet_age_unix
            days = age_seconds // (24 * 60 * 60)
            if days < 7:
                message_parts.append(f"🔴 ")#(https://solscan.io/account/{wallet['wallet']})")
            elif days < 30:
                message_parts.append(f"🟠 ")#(https://solscan.io/account/{wallet['wallet']})")
            elif days < 90: 
                message_parts.append(f"🟡 ")#(https://solscan.io/account/{wallet['wallet']})")
            else:
                message_parts.append(f"🟢 ")#(https://solscan.io/account/{wallet['wallet']})")
            count+=1

        msg =  ''.join(message_parts)
        return msg
async def fresh_wallets_v2_parsed(token, limit):
    data = await fresh_wallets_v2(token, limit)
    token_info = data['token_info']
    valid_results = data['valid_results']
    items = data['items']
    token_symbol = token_info['symbol']
    token_name = token_info['name']
    market_cap = format_number(token_info['market_cap'])
    liquidity = format_number(token_info['liquidity'])
    holder = format_number(token_info['holder'], with_dollar_sign=False)
    socials = generate_socials_message(token_info, token)
    message_parts = [
        f"*Token*: {token_symbol} ({token_name})\n",
        f"├──💰 MC: {market_cap}\n",
        f"├──💦 Liquidity: {liquidity}\n",
        f"├──👥 Holders count: {holder}\n",
        f"Fresh Wallets {valid_results}/{limit}: \n\n",
        socials
    ]
    for item in items:
        if 'error' in item:
            continue
        elif item['funding_source']:
            message_parts.append(f"🌿#{item['count']}\\({shorten_address(item['address'])}\\) {item['holding_pct']}% funded by {shorten_address(item['funding_source'])}\n")

    
    msg = ''.join(message_parts)
    return msg


async def top_holders_net_worth_map(token, limit):
    if running:
        data = await get_top_holders_holdings(token, limit)

        token_info =  data['token_info']
        top_holders= data ['items']

    else:
        print ('parsing from json')

        data = json.load(open("backend/commands/outputs/top_holders_holdings.json", 'r'))
        
        token_info =  data['token_info']
        top_holders= data ['items']


    #print(token_info)
    print(len(top_holders))
    # Token information part=
   # Token information part=
    message = "Top Net Worth Map by EL MUNKI 🐵🌕:\n\n"

    message += f"*Token Info*: {token_info['symbol']} \\({token_info['name']}\\)\n"
    message += f"├──💰MC: {format_number(token_info['market_cap'])}\n"
    message += f"├──🫗Liquidity: {format_number(token_info['liquidity'])}\n"
    message += f"├──👥Holders count: {token_info['holder']:,}\n\n"
    #message += f"├──[*X*]({token_info['twitter']})──[*WEB*]({token_info['website']})──[📊*CHART*](https://dexscreener.com/solana/{token})\n"


    c = 1
    whale = 0
    shark = 0
    dolphin = 0
    fish = 0
    shrimp = 0
    foam = 0
    for holder in top_holders:
        if 'error' in holder or 'net_worth_excluding' not in holder:
            print (holder)
            continue

        net_worth = holder['net_worth_excluding']
        if net_worth > 100_000:
            message += "🐳"
            whale += 1
            if c%10 == 0:
                message += "\n"

        elif net_worth > 10_000:
            message += "🦈"
            shark += 1
            if c%10 == 0:
                message += "\n"

        elif net_worth > 1_000:
            message += "🐬"
            dolphin += 1
            if c%10 == 0:
                message += "\n"

        elif net_worth > 100:
            message += "🐟"
            fish += 1
            if c%10 == 0:
                message += "\n"
        elif net_worth > 10:
            message += "🦐"
            shrimp += 1
            if c%10 == 0:
                message += "\n"
        else:
            message += "🫧"
            foam += 1
            if c%10 == 0:
                message += "\n"
        c+=1    

    holder_counts = {
        "🫧 (<$10)": foam,
          "🦐 (<$100)": shrimp,
        "🐟 ($100-$1k)": fish,
        "🐬 ($1k-$10k)": dolphin,
        "🦈 ($10k-$100k)": shark,
        "🐳 ($100k+)": whale
            }
    message += "\n\n"
    message += f"*Summary of Top {limit} Holders net worth excluding {token_info['symbol']} \\({token_info['name']}\\)*\n"

    for emoji, count in holder_counts.items():
        message += escape_markdown(f"{emoji}:  {count}\n") 

    return message





async def noteworthy_addresses_parsed(token, limit):

    """
    Parses and formats the data for MarkdownV2 compatibility, returning an array of strings with each
    string having a maximum of 4096 characters.
    """
   
    if running:
        data = await(get_noteworthy_addresses(token, limit))
        token_info = data['token_info']
        items = data['items']

    else:
        print ('parsing from json')

        data = json.loads(open("backend/commands/outputs/noteworthy_addresses.json", 'r').read())# for testing
        token_info = data['token_info']
        items = data['items']

    # Escape token info for MarkdownV2
    token_symbol = escape_markdown(token_info['symbol'])
    token_name = escape_markdown(token_info['name'])
    market_cap = format_number(token_info['market_cap'])
    liquidity = format_number(token_info['liquidity'])
    holder = format_number(token_info['holder'])
    print (type(token_info['priceChange1hPercent']))
    priceChange1hPercent = escape_markdown(f"{token_info['priceChange1hPercent']:.2f}")

    if priceChange1hPercent[0] !=  "-":
        change = f"├──🟢 1H Change: {priceChange1hPercent}%\n\n"
    else:
        change = f"├──🔴 1H Change: {priceChange1hPercent}%\n\n"
    # Create the message header
    message_parts = [
        f"*Token*: {token_symbol} \\({token_name}\\)\n",
        f"├──💰 MC: {market_cap}\n",
        f"├──💦 Liquidity: {liquidity}\n",
        f"├──👥 Holders count: {holder}\n",
        change,
        f"*{data['valid_results']}/{limit} Noteworthy Addresses*:\n\n"
    ]

    chunks = []  # To store the resulting chunks
    current_chunk = "".join(message_parts)  # Start with the header

    for item in items:
        if 'error' in item:
            continue

        wallet = item['wallet']
        short_wallet = escape_markdown(shorten_address(wallet))
        addy = escape_markdown(f"https://solscan.io/account/{wallet}")
        networth_excl = format_number(item['net_worth_excluding'])

        # Build the individual message for the wallet
        message = f"\\#{item['count']}🐋 [{short_wallet}]({addy}) \\| "

        top_trader = item.get('top_trader', {})
        if top_trader:
            message += f"🔝Trader"

        # Add holdings information
        if 'first_top_holding' in item:
            top1 = item['first_top_holding']
            top1_symbol = escape_markdown(top1['symbol'])
            top1_address = escape_markdown(top1['address'])
            top1_value = format_number(top1['valueUsd'])
            message += f"[{top1_symbol}]({top1_address}): {top1_value}, "

        if 'second_top_holding' in item:
            top2 = item['second_top_holding']
            top2_symbol = escape_markdown(top2['symbol'])
            top2_address = escape_markdown(top2['address'])
            top2_value = format_number(top2['valueUsd'])
            message += f"[{top2_symbol}]({top2_address}): {top2_value}, "

        if 'third_top_holding' in item:
            top3 = item['third_top_holding']
            top3_symbol = escape_markdown(top3['symbol'])
            top3_address = escape_markdown(top3['address'])
            top3_value = format_number(top3['valueUsd'])
            message += f"[{top3_symbol}]({top3_address}): {top3_value}"

        # Add the wallet message to the chunk or create a new chunk if needed
        if len(current_chunk) + len(message) + 2 > 4096:  # +2 for the newline
            chunks.append(current_chunk)
            current_chunk = message + " \n"
        else:
            current_chunk += message + " \n"

    # Append the last chunk if it contains data
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


if __name__ == "__main__":
    time_now = time.time()
    print(asyncio.run(fresh_wallets_v2_parsed("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump", 100)))
    print("Execution time:", time.time() - time_now, "seconds")
    # print(asyncio.run(holder_distribution_parsed("9XS6ayT8aCaoH7tDmTgNyEXRLeVpgyHKtZk5xTXpump")))i

#     token_info = '{"symbol": "OBOT", "name": "OBOT", "logoURI": "https://ipfs.io/ipfs/QmeeSqjjrpQ5ht5uc21uG3j3PdVM46CkfTXUCyt23vs462", "liquidity": 1042030.2735918732, "market_cap": 8623704.06309531}'
#     token_info = json.loads(token_info)
#     timenow = float(time.time())
#     print(token_info)

#     def find_unescaped_periods(text, context_length=10):
#         """
#         Find unescaped periods (.) in a string and show context around them.
        
#         Args:
#             text (str): The input string to search.
#             context_length (int): Number of characters to show before and after the match.
        
#         Returns:
#             List of tuples: Each tuple contains (match_position, context_before, match, context_after).
#         """
#         # Regex pattern to match unescaped periods
#         pattern = r"(?<!\\)\."
        
#         # Find all matches
#         matches = []
#         for match in re.finditer(pattern, text):
#             start = match.start()
#             end = match.end()
            
#             # Extract context before and after the match
#             context_before = text[max(0, start - context_length):start]
#             context_after = text[end:min(len(text), end + context_length)]
            
#             # Append the match and its context to the results
#             matches.append((start, context_before, match.group(), context_after))
        
#         return matches  
    
#     BOT_TOKEN = os.environ.get('tgTOKEN')



# # Replace 'USER_CHAT_ID' with the chat_id of the user you want to send the message to
#     USER_CHAT_ID = 6313106291 # Example chat_id

# # Initialize the bot
#     message = asyncio.run(top_holders_holdings_parsed('www',20))
# #    unescaped_characters = []
# #    for i in range (len (message)) :
# #        unescaped_characters.append ((find_unescaped_periods(message[i])))
# #

# #
# #
# #
# #    print (message)
# #    print (unescaped_characters)
#     for i in range(0, len(message)):
#         asyncio.run(send_message(BOT_TOKEN, USER_CHAT_ID, message[i]))
# #
#     message, something = asyncio.run(holder_distribution_parsed('www'))
# #    asyncio.run(send_message(BOT_TOKEN, USER_CHAT_ID, message))
# #    message = fresh_wallets_parsed('www',20)
# #    print (message) 
#     print (message)
#     asyncio.run(send_message(BOT_TOKEN, USER_CHAT_ID, message))
#     message = asyncio.run(top_holders_net_worth_map('www',20))
#     asyncio.run(send_message(BOT_TOKEN, USER_CHAT_ID, message))
    
#     message = asyncio.run(noteworthy_addresses_parsed('www',20))

#     for i in range(0, len(message)):
#         asyncio.run(send_message(BOT_TOKEN, USER_CHAT_ID, message[i]))


# # Send a message to the user
#      #array_of_objects = ast.literal_eval(data)
#     #print(array_of_objects)

#     # Convert each dictionary in the list to a JSON string
#     #array_of_json = [json.dumps(d) for d in array_of_objects]

    
#     #holders = asyncio.run(top_holders_holdings_parsed(token_info, array_of_objects))

#    # print (holders)
#    #  import telegram
#    #  import os
#    #  import telebot
#    #  token = os.environ.get('tgbot')
#    # 
#    #  if not token:
#    #      raise ValueError("Bot token not found in environment variables")
#    #  
#    #  bot = telebot.TeleBot(token)
#    #  chat_id = os.environ.get('tgchat')
#    #  if len(holders) > 4096:
#    #      for text in split_message(holders):
#    #          bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.constants.ParseMode.MARKDOWN)
#    #  else:
#    #      bot.send_message(chat_id=chat_id, text=holders)
#    #  
#     #print(asyncio.run(get_wallet_portfolio("GitBH362uaPmp5yt5rNoPQ6FzS2t7oUBqeyodFPJSZ84")))
#     # fresh_wallets = asyncio.run(fresh_wallets("7yZFFUhq9ac7DY4WobLL539pJEUbMnQ5AGQQuuEMpump", 50))
#     # print((fresh_wallets[1]))
#     # print(fresh_wallets_parsed(fresh_wallets[0], fresh_wallets[1]))
#     # print(float(time.time()) - timenow)
