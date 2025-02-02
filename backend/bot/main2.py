import asyncio
from typing import Final
from telegram import Bot, Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext 
from .tg_commands import *
from db.chat.log import log_chat
# from ...db.user.log import log_user
import os 
import json
from .parser import *
from .log import log_tamago
import asyncio
import traceback
limit = 50 #to change

TOKEN= os.environ.get('tgTOKEN')
BOT_USERNAME= os.environ.get('tgNAME')   # tgNAME
if not TOKEN:
    TOKEN = os.environ.get('tgbot')
PORT = int(os.environ.get('PORT', 8443))
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text"""
    query = update.callback_query
    await query.answer()  # Note: Use 'await' if your bot uses 'async' methods

    if query.data == "/check":  # Make sure this matches your callback_data
        text = await check_renew(update, context) 
    # Make sure this matches your callback_data

    else:
        text = "Unknown option!"

    await query.message.reply_text(text)
#handle responnses
def handle_response(text:str ) -> str:
    processed : str =text.lower()
    if processed == 'hello':
        return 'To use this bot please enter one of the commands from /help in the chat.'
    else:
        return 'I have no idea what you want please use /help to explore my functions.'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print (f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if 1:#context.user_data.get('awaiting_token_address', False):
        # Let the token address handler process this message
        await handle_token_address(update, context)
        return

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text. replace (BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:   
            return
    else:
        response: str = handle_response(text)

    log_tamago(update, response)
    print('Bot:', response)
    await update.message.reply_text(response)

async def handle_token_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_token_address'] = False
    token_address = update.message.text.strip()

    # Validate token address
    if len(token_address) < 43:  # Adjust this check for Solana addresses
        await update.message.reply_text("Invalid token address. Please try again with a valid address.")
        return
    command = ''
    # Store the token address in user_data
    holder_message = None
    # Check if 'top_holders_started' exists and is set, otherwise default to False
    if context.user_data.get('top_holders_started', False):
        context.user_data['top_holders_started'] = False
        command = 'top'
        wait_message = await update.message.reply_text("Analyzing top holders please chill...")
        holder_message = await top_holders_holdings_parsed(token_address, limit)

    elif context.user_data.get('net_worth_map_started', False):
        wait_message = await update.message.reply_text("Checking for whales please chill...")
        command = 'map'
        context.user_data['net_worth_map_started'] = False
        holder_message = await top_holders_net_worth_map(token_address, limit)

    # Check if 'token_distribution_started' exists and is set, otherwise default to False
    elif context.user_data.get('token_distribution_started', False):
        wait_message = await update.message.reply_text("Checking for holder distribution please chill...")
        command = 'distrubtion'
        context.user_data['token_distribution_started'] = False
        holder_message = await holder_distribution_parsed(token_address)

    elif context.user_data.get('fresh_wallets_started', False): 
        wait_message = await update.message.reply_text("Checking for fresh wallets please chill...")
        command = 'fresh'
        context.user_data['fresh_wallets_started'] = False
        holder_message = await fresh_wallets_parsed(token_address, limit)
    elif context.user_data.get('avg_entry_started', False):
        wait_message = await update.message.reply_text("Checking for average entry price please chill...")
        command = 'avg'
        context.user_data['avg_entry_started'] = False
        holder_message = await holders_avg_entry_price_parsed(token_address, limit)
    else: 
        try: 
            wait_message = await update.message.reply_text("Analyzing token getting top holders please chill...")
            command = 'top'
            holder_message = await top_holders_holdings_parsed(token_address, max(limit-20, 0))
        except Exception as e:
            print(e)
            await update.message.reply_text("Something went wrong, please contact support.")

    await log_chat(update.message.chat.id, update.message.chat.username, command, token_address, update.message.__str__())
    print(holder_message)
    parse_mode = 'MarkdownV2'
    if command == 'avg':
        parse_mode = 'Markdown'
    if type(holder_message) == list:
        for parts in holder_message:
            if parts == holder_message[0]:
                await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=wait_message.message_id,
                text=parts
                , parse_mode=parse_mode, disable_web_page_preview=True)
            else:
                await update.message.reply_text(parts , parse_mode=parse_mode, disable_web_page_preview=True)
    else:
        await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=wait_message.message_id,
                text=holder_message
                , parse_mode=parse_mode, disable_web_page_preview=True)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    print (f'Update {update} caused error {context.error}')
    print("Traceback:")
    traceback.print_exc()
    await update.message.reply_text("Something went wrong, please contact support.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:   
    response = '''/top - top [contract adress] to get list of topholders
/userid - get your userid 
/renew - renew your subscription
/referral - get referral link
/fresh - [contract adress] to get a list of fresh wallets
/sub - get subscription status
/map - [contract adress] get map of net worth of top holders

    '''
    log_tamago(update, response=response)
    await update.message.reply_text(f'{response}')
async def delete_webhook(TOKEN):
    bot = Bot(TOKEN)
    await bot.delete_webhook()

def main():
    print ('start_command')
    app = Application.builder().token(TOKEN).build()

    #Commands
    #main functions
    app.add_handler(CommandHandler('top', topholders_command))
    app.add_handler(CommandHandler('fresh', fresh_wallets_command))
    app.add_handler(CommandHandler('map', top_net_worth_map_command))
    app.add_handler(CommandHandler('avg', avg_entry_command))
    #user functions
    app.add_handler(CommandHandler('userid', userid_command))
    app.add_handler(CommandHandler('renew', renew_command))
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('referral', referrallink_command))
    app.add_handler(CommandHandler('sub', check_subscription))
    app.add_handler(CommandHandler('help', help))

    #Buttons

    app.add_handler(CallbackQueryHandler(handle_buttons))
    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #Error
    app.add_error_handler(error)
    #Set Webhook
    if HEROKU_APP_NAME:
        webhook_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}'
        print (webhook_url)
        print (PORT)
        print(f"Webhook set to: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url,
        )
    else:
        print('Polling locally (webhook removed)')
              # Remove any existing webhook explicitly
        #asyncio.run(app.bot.delete_webhook()  )# Ensure this is awaited
        delete_webhook(TOKEN)

        app.run_polling(poll_interval=3)



# webhook 

if __name__ == "__main__":
    main()

