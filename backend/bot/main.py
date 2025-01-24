import os
from telegram import BotCommand
import telebot
from .log import log_entry
from backend.commands.holding_distribution import get_holding_distribution
from backend.commands.top_holders_holdings import get_top_holders_holdings
from backend.commands.noteworthy_addresses import get_noteworthy_addresses

from .parser import top_holders_holdings_parsed, fresh_wallets_parsed, holder_distribution_parsed, noteworthy_addresses_parsed
from telegram.constants import ParseMode
import asyncio
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO
import time
TOP_HOLDERS_LIMIT=20
# Add error handling for missing token
token = os.environ.get('tgbot')
if not token:
    raise ValueError("Bot token not found in environment variables")

bot = telebot.TeleBot(token)

# A dictionary to track user states
user_states = {}

# States
STATE_WAITING_FOR_TOKEN = "WAITING_FOR_TOKEN"

MAX_MESSAGE_LENGTH = 4096

def split_message(text):
    return [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]



def fetch_image_as_sticker(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Retry mechanism for handling rate-limiting (HTTP 429)
        retries = 5
        while retries > 0:
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code == 429:  # Too many requests
                print("Rate limited. Retrying...")
                retries -= 1
                time.sleep(1)  # Wait before retrying
            else:
                response.raise_for_status()  # Raise for other HTTP errors
                break
        else:
            raise Exception("Failed to fetch the image after multiple retries due to rate-limiting.")

        # Load the image
        image_data = BytesIO(response.content)
        try:
            image = Image.open(image_data)
        except UnidentifiedImageError:
            raise ValueError("The URL does not contain a valid image.")

        # Resize the image to 50% of its original size
        width, height = image.size
        new_size = (int(width * 0.5), int(height * 0.5))
        image = image.resize(new_size, Image.Resampling.LANCZOS)  # Resize with anti-aliasing for better quality

        # Handle animated images (GIFs)
        if getattr(image, "is_animated", False):
            sticker_data = BytesIO()
            image.save(sticker_data, format="WEBP", save_all=True)
            sticker_data.seek(0)
        else:
            # Non-animated image handling
            sticker_data = BytesIO()
            image.convert("RGBA").save(sticker_data, format="WEBP")
            sticker_data.seek(0)

        return sticker_data

    except Exception as e:
        print(f"An error occurred: {e}") 
        return None
#/start
def handle_start(message):
    """
    Handle the /start command.
    """
    command = "start"
    log_entry(command=command, entry=message, content={})
    bot.reply_to(message, "Hello! How can I assist you today?")
#/help
def handle_help(message):
    """
    Handle the /help command.
    """
    command = "help"
    log_entry(command=command, entry=message, content={})
    bot.reply_to(message, "Here are some commands you can use:\n" +
                          "/top_holders\n" +
                          "/top_holders_avg\n" +
                          "/top_traders\n" +
                          "/whales_or_kols\n" +
                          "/token_dist\n" +
                          "/holders_age\n" +
                          "/noteworthy_addresses\n") 
#/top_holders
def handle_top_holders(message):
    """
    Handle the /top_holders command.
    """
    bot.reply_to(message, "Please provide the token address (Solana):")
    user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "top_holders"}
#/top_holders_avg
def handle_top_holders_avg(message):
    """
    Handle the /top_holders_avg command.
    """
    bot.reply_to(message, "Please provide the token address for average holding calculation:")
    #user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "top_holders_avg"}
#/top_traders
def handle_top_traders(message):
    """
    Handle the /top_traders command.
    """
    bot.reply_to(message, "Please provide the token address to fetch top traders:")
    #user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "top_traders"}
#/whales_or_kols
def handle_whales_or_kols(message):
    """
    Handle the /whales_or_kols command.
    """
    bot.reply_to(message, "Please provide the token address to analyze whales or KOLs:")
    #user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "whales_or_kols"}
#/token_dist
def handle_token_dist(message):
    """
    Handle the /token_dist command.
    """
    bot.reply_to(message, "Please provide the token address to analyze distribution:")
    user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "token_dist"}
#/holders_age
def handle_holders_age(message):
    """
    Handle the /holders_age command.
    """
    bot.reply_to(message, "Please provide the token address to analyze holder wallet ages:")
    user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "holders_age"}
#/noteworthy_addresses
def handle_noteworthy_addresses(message):
    """
    Handle the /noteworthy_addresses command.
    """
    bot.reply_to(message, "Please provide the token address to fetch noteworthy addresses:")
    user_states[message.chat.id] = {"state": STATE_WAITING_FOR_TOKEN, "command": "noteworthy_addresses"}

# Handle token response
def handle_token_response(message):
    """
    Handle the user's response after providing a token address.
    """
    user_state = user_states.get(message.chat.id)
    if not user_state or user_state["state"] != STATE_WAITING_FOR_TOKEN:
        return

    command = user_state["command"]
    token_address = message.text.strip()
    print("Processing command:", command, "for token:", token_address)
    match command:
        case "top_holders":
            # Get the top holders of a token
            if 32>len(token_address)>44:
                bot.reply_to(message, "Invalid token address. Please provide a valid Solana token address.")
            else:
                reply = top_holders_holdings_parsed(token_address, TOP_HOLDERS_LIMIT)
                if len(reply) > MAX_MESSAGE_LENGTH:
                    for part in split_message(reply):
                        bot.reply_to(message, part, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                else:
                    bot.reply_to(message, reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                user_states.pop(message.chat.id, None)
        case "holders_age":
            # Get the holder wallet ages
            if 32>len(token_address)>44:
                bot.reply_to(message, "Invalid token address. Please provide a valid Solana token address.")
            else:
                reply = fresh_wallets_parsed(token_address, TOP_HOLDERS_LIMIT)
                print(reply)
                bot.reply_to(message, reply , parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                user_states.pop(message.chat.id, None)
        case "token_dist":
            # Get the distribution of a token
            if 32>len(token_address)>44:
                bot.reply_to(message, "Invalid token address. Please provide a valid Solana token address.")
            else:
                reply, url = asyncio.run (holder_distribution_parsed(token_address))
                bot.reply_to(message,reply,parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                sticker = fetch_image_as_sticker(url)
                if sticker:
                    bot.send_sticker(message.chat.id, sticker)
                user_states.pop(message.chat.id, None)
        case "noteworthy_addresses":
            # Get noteworthy addresses
            if 32>len(token_address)>44:
                bot.reply_to(message, "Invalid token address. Please provide a valid Solana token address.")
            else:
                replies = noteworthy_addresses_parsed(token_address, 0)
                for reply in replies:
                    bot.reply_to(message, reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                user_states.pop(message.chat.id, None)
        case _:
            bot.reply_to(message, "still in development")
            user_states.pop(message.chat.id, None)
    # Log and respond based on the command
    log_entry(command=command, entry=message, content={"token": token_address})
    # Clear user state
    

# Command Router
command_handlers = {
    "start": handle_start,
    "help": handle_help,
    "top_holders": handle_top_holders,
    "top_holders_avg": handle_top_holders_avg,
    "top_traders": handle_top_traders,
    "whales_or_kols": handle_whales_or_kols,
    "token_dist": handle_token_dist,
    "holders_age": handle_holders_age,
    "noteworthy_addresses": handle_noteworthy_addresses,
}

@bot.message_handler(commands=list(command_handlers.keys()))
def route_command(message):
    """
    Route commands to their respective handlers.
    """
    
    command = message.text.split()[0][1:]  # Remove the leading slash
    if command in command_handlers:
        print(f"Command {command} received from {message.from_user.username}")
        command_handlers[command](message)

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("state") == STATE_WAITING_FOR_TOKEN)
def route_token_response(message):
    """
    Route messages when the bot is waiting for a token address.
    """
    handle_token_response(message)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    """
    Echoes any other message sent to the bot.
    """
    bot.reply_to(message, "I didn't recognize that command. Use /help to see the available commands.")

# Set Bot Commands
def set_bot_commands():
    """
    Sets the bot commands with descriptions for Telegram UI.
    """
    commands = [
        BotCommand("start", "Start interacting with the bot"),
        BotCommand("help", "Get help about the bot"),
        BotCommand("top_holders", "Get the detailed top holders of a token"),
        BotCommand("top_holders_avg", "Get the average holdings of top holders"),
        BotCommand("top_traders", "Check if topp traders are holding"),
        BotCommand("whales_or_kols", "Analyze whales or KOLs"),
        BotCommand("token_dist", "Get the distribution of a token"),
        BotCommand("holders_age", "Get a heatmap of holder wallets ages"),
    ]
    bot.set_my_commands([telebot.types.BotCommand(c.command, c.description) for c in commands])

if __name__ == "__main__":
    set_bot_commands()
    print("Bot started")
    bot.infinity_polling()
