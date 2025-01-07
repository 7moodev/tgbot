import os
from telegram import tl_notify, tl_notify_group
import telebot
from log import log_entry
# Add error handling for missing token
token = os.environ.get('tgbot')
if not token:
    raise ValueError("Bot token not found in environment variables")

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    command = message.text.split()[0]
    content = message.text.split()[1:]
    print(command)
    print(content)
    log_entry(command=command[1:],entry=message, content=content)
    # Get everything after the command by splitting and joining remaining words
    command_text = ' '.join(message.text.split()[1:])
    print(message)
    print(f"Text after command: {command_text}")
    """
    Handle the /start command and send a welcome message.
    Args:
        message: The message object from Telegram
    """
    bot.reply_to(message, "Hello, how can I help you today?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text) 
    
if __name__ == '__main__':

    # Start the bot
    print("started")
    bot.infinity_polling()

