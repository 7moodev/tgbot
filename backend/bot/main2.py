from typing import Final
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext 
from .tg_commands import *
import os 
from .parser import top_holders_holdings_parsed, holder_distribution_parsed

TOKEN= os.environ.get('tgTOKEN')
BOT_USERNAME= "@VNFlybot"
PORT = int(os.environ.get('PORT', 5000))
HEROKU_APP_NAME = os.environ.get('munki-tg-bot')

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

    if context.user_data.get('awaiting_token_address', False):
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

    print('Bot:', response)
    await update.message.reply_text(response)

async def handle_token_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_token_address'] = False
    token_address = update.message.text.strip()

    # Validate token address
    if len(token_address) < 43:  # Adjust this check for Solana addresses
        await update.message.reply_text("Invalid token address. Please provide a valid address.")
        return

    # Store the token address in user_data
    holder_message = None

    # Check if 'top_holders_started' exists and is set, otherwise default to False
    if context.user_data.get('top_holders_started', False):
        context.user_data['top_holders_started'] = False
        holder_message = await top_holders_holdings_parsed(token_address, limit=20)
    
    # Check if 'token_distribution_started' exists and is set, otherwise default to False
    elif context.user_data.get('token_distribution_started', False):
        context.user_data['token_distribution_started'] = False
        holder_message = await holder_distribution_parsed(token_address)

    print(holder_message)
    await update.message.reply_text(holder_message, parse_mode='MarkdownV2', disable_web_page_preview=True)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    print (f'Update {update} caused error {context.error}')



# webhook 

if __name__ == "__main__":
    print ('start_command')
    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('distro', token_distribution_command))
    app.add_handler(CommandHandler('top', topholders_command))
    app.add_handler(CommandHandler('userid', userid_command))
    app.add_handler(CommandHandler('renew', renew_command))
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('referal', referrallink_command))
    app.add_handler(CommandHandler('sub', check_subscription))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #Error
    app.add_error_handler(error)


    #Set Webhook
    webhook_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}'
    bot = Bot(TOKEN)
    bot.set_webhook(webhook_url)
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url,
    )

    #print ('polling')
    #app.run_polling(poll_interval=3)


