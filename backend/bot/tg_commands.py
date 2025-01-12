from .paywall.payment import *
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext 
from .parser import top_holders_holdings_parsed, holder_distribution_parsed

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.chat.id 
    args = context.args
    referral_info = None

    if len(args):
        referral_info = args[0]

    s = check_user(user_id, referral_info )
    # Define keyboard layout
    await update.message.reply_text("Welcome use /help to explore the commands.")

async def referrallink_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.chat.id
    bot_name =  BOT_USERNAME[1:]
    referral_link = f"https://t.me/{bot_name}?start=ref_{user_id}"
   

 
    # Define keyboard layout
    await update.message.reply_text(f"Your refferal link is: \n {referral_link}")

async def topholders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['top_holders_started'] = True 
            return

        else:
            token_address = context.args[0]
            holder_message = await top_holders_holdings_parsed(token_address, limit = 20)
            print (holder_message)


            await update.message.reply_text(holder_message , parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')

async def token_distribution_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['token_distribution_started'] = True 
            return

        else:
            token_address = context.args[0]
            holder_message = await holder_distribution_parsed(token_address)
            print (holder_message)


            await update.message.reply_text(holder_message , parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')




async def userid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'{update.message.chat.id}')

public_key = 'test'

async def renew_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    info = get_user_info(user_id)

    if check_access(user_id):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You already have an active subscription expiring {time_left}'
        await update.message.reply_text(f'{response}')
    
    else: 
        public_key = info["public_key"]
        keyboard = [
        [ InlineKeyboardButton("Check", callback_data='/check') ]
        ]
        # Create the reply markup with the above keyboard layout
        reply_markup = InlineKeyboardMarkup(keyboard)
        renew_message = f'''Thanks for deciding to renew your subscription!
    Monthly subscriptions are 1 SOL a month. Please deposit 1 SOL to the following address:
    {public_key}
    After you have sent the funds, please click the Check button below.'''

        # Send message with the keyboard
        # await update.message.reply_text(f'{renew_message}')
        await update.message.reply_text(f'{renew_message}', reply_markup=reply_markup)
    
async def check_renew(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.callback_query.message.chat.id
    # Here, you would replace 'check_payment' with whatever function checks for check_payment
    response = grant_access(str(user_id))
        #await update.message.reply_text(f'{response}')
    await update.callback_query.message.reply_text(response)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.callback_query.message.chat.id
    # Here, you would replace 'check_payment' with whatever function checks for check_payment
    
    info = get_user_info(user_id)
    if check_access(user_id):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You have an active subscription expiring {time_left}'
        #await update.message.reply_text(f'{response}')
        await update.callback_query.edit_message_text(text=response)

    else:
        response = f'No subscription active. Use /renew to buy a subscription.'

        #await update.message.reply_text(f'{response}')
        await update.callback_query.edit_message_text(text=response)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:   
    response = '''
    /top - top [contract adress] to get list of topholders 
    /userid - get your userid 
    /renew - renew your subscription
    /referal - get referal link
    /sub - get subscription status
    /distro - [contract adress] get distribution of token holders
    '''
    await update.message.reply_text(f'{response}')
