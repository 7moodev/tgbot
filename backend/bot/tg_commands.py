from .paywall.payment import *
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext 
from .parser import fresh_wallets_v2_parsed, noteworthy_addresses_parsed, top_holders_holdings_parsed, holder_distribution_parsed, get_noteworthy_addresses, top_holders_net_worth_map, fresh_wallets_parsed, holders_avg_entry_price_parsed
from db.chat.log import log_chat
import time
BOT_USERNAME= os.environ.get('tgNAME') 
if not BOT_USERNAME:
    BOT_USERNAME = "ALM_NotifyBot"  # tgNAME 
limit = 50
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.chat.id 
    args = context.args
    referral_info = None
    if len(args):
        referral_info = args[0]
    print (referral_info)

    s = check_user(user_id, referral_info )
    # Define keyboard layout
    msg = """Welcome to EL MUNKI 🐵🌕 you horny degen! This is your personal Memecoin Analytics Tool.
Get started by using the commands below:
\nSend /top [contract address] to get analytics on the top holders
Send /map [contract address] to get a map of the top holders
Send /fresh [contract address] to get fresh wallets list
Send /avg [contract address] to get avg holding price among top holders
Send /sub to see you subscription status
Send /renew to renew your subscription"""
    await update.message.reply_text(msg)
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
            
            wait_message = await update.message.reply_text("Analyzing token and getting top holders please chill...")
            time_now = float(time.time())
            message = await top_holders_holdings_parsed(token_address, limit )
            #print (message)
            if type(message) == str:
                log_message = message
            else:
                log_message = message[0]
            await log_chat(user_id, update.message.chat.username, "top", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
            for parts in message:
                if parts == message[0]:
                    await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=parts
                    , parse_mode='MarkdownV2', disable_web_page_preview=True)
                else:
                    await update.message.reply_text(parts , parse_mode='MarkdownV2', disable_web_page_preview=True)

    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')

async def avg_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['avg_entry_started'] = True 
            return 
        else:
            token_address = context.args[0]
            wait_message = await update.message.reply_text("Analyzing token and getting avg entry, please chill...")
            time_now = float(time.time())
            message = await holders_avg_entry_price_parsed(token_address, limit )
            if type(message) == str:
                log_message = message
            else:
                log_message = message[0]
            await log_chat(user_id, update.message.chat.username, "avg", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
          
            #print (message)
            for parts in message:
                if parts == message[0]:
                    await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=parts
                    , parse_mode='MarkdownV2', disable_web_page_preview=True)
                else:
                    await update.message.reply_text(parts , parse_mode='MarkdownV2', disable_web_page_preview=True)

    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')


async def top_net_worth_map_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['net_worth_map_started'] = True 
            return

        else:
            token_address = context.args[0]
            time_now = float(time.time())
            wait_message = await update.message.reply_text("Analyzing token and looking for Whales please chill...")
            message = await top_holders_net_worth_map(token_address, limit )
            if type(message) == str:
                log_message = message
            else:
                log_message = message[0]
            await log_chat(user_id, update.message.chat.username, "map", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
            #print (message)

            await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=message
                    , parse_mode='MarkdownV2', disable_web_page_preview=True)


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
            time_now = float(time.time())
            holder_message = await holder_distribution_parsed(token_address)
            if type(holder_message) == str:
                log_message = holder_message
            else:
                log_message = holder_message[0]
            await log_chat(user_id, update.message.chat.username, "dist", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
            #print (holder_message)

            await update.message.reply_text(holder_message , parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')

async def fresh_wallets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['fresh_wallets_started'] = True 
            return

        else:
            token_address = context.args[0]
            time_now = float(time.time())
            wait_message = await update.message.reply_text("Looking for Fresh Wallets please chill...")
            holder_message = await fresh_wallets_v2_parsed(token_address, limit)
            if type(holder_message) == str:
                log_message = holder_message
            else:
                log_message = holder_message[0]
            await log_chat(user_id, update.message.chat.username, "fresh", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
           # print (holder_message)
            await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=holder_message
                    , parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')


async def wallets_age_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['wallets_age_started'] = True 
            return

        else:
            token_address = context.args[0]
            time_now = float(time.time())
            wait_message = await update.message.reply_text("Checking top holders experience please chill...")
            holder_message = await fresh_wallets_parsed(token_address, limit)
            if type(holder_message) == str:
                log_message = holder_message
            else:
                log_message = holder_message[0]
            await log_chat(user_id, update.message.chat.username, "fresh", token_address,update.message.__str__(),log_message, float(time.time())-time_now)
            #print (holder_message)
            await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=holder_message
                    , parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')




async def userid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'{update.message.chat.id}')


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
        renew_message = escape_markdown(f'''Thanks for deciding to renew your subscription!
    Monthly subscriptions are 0.69 SOL a month in our beta phase. Please deposit 0.69 SOL to the following address:
    `{public_key}`
    After you have sent the funds, please click the Check button below.''')

        # Send message with the keyboard
        # await update.message.reply_text(f'{renew_message}')
        await update.message.reply_text(f'{renew_message}', reply_markup=reply_markup, parse_mode='MarkdownV2')
    
async def check_renew(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.callback_query.message.chat.id
    # Here, you would replace 'check_payment' with whatever function checks for check_payment
    response = grant_access(str(user_id))
        #await update.message.reply_text(f'{response}')
    await update.callback_query.message.reply_text(response)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.message.chat.id
    check_message = await update.message.reply_text("Checking Subscription Status...")
    # Here, you would replace 'check_payment' with whatever function checks for check_payment
    info = get_user_info(user_id)
    if check_access(user_id):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You have an active subscription expiring {time_left}'
        #await update.message.reply_text(f'{response}')
  
    else:
        response = f'No subscription active. Use /renew to buy a subscription.'

        #await update.message.reply_text(f'{response}')
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=check_message.message_id,
        text=response)

