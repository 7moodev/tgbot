from backend.xBot.x_bot import process_ca_and_post_to_x
from .paywall.payment import *
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext 
from .log import log_tamago
from .parser import *
from db.chat.log import log_chat
import backend.bot.exc as exc
import time
BOT_USERNAME= os.environ.get('tgNAME') 
if not BOT_USERNAME:
    BOT_USERNAME = "ALM_NotifyBot"  # tgNAME 
limit = 50
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.chat.id
    tg_username= update.message.chat.username
    args = context.args
    referral_info = None
    if len(args):
        referral_info = args[0]
    print (referral_info)

    s = check_user(user_id, referral_info, tg_username )
    # Define keyboard layout
    msg = """Welcome to EL MUNKI 🐵🌕 you horny degen! This is your personal Memecoin Analytics Tool.
Get started by using the commands below:
\nSend /top [contract address] to get analytics on the top holders
Send /map [contract address] to get a map of the top holders
Send /fresh [contract address] to get fresh wallets list
Send /avg [contract address] to get avg holding price among top holders
Send /sub to see you subscription status
Send /renew to renew your subscription"""
    log_tamago(update)
    await update.message.reply_text(msg)
async def referrallink_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.chat.id
    bot_name =  BOT_USERNAME[1:]
    referral_link = f"https://t.me/{bot_name}?start=ref_{user_id}"
    # Define keyboard layout
    log_tamago(update, response=referral_link)
    await update.message.reply_text(f"Your referral link is: \n {referral_link}")
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

            try:
                for parts in message:
                    if parts == message[0]:
                        log_tamago(update, response=parts)
                        await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=wait_message.message_id,
                        text=parts
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    else:
                        log_tamago(update, response=parts)
                        await update.message.reply_text(parts , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    await log_chat(user_id, update.message.chat.username, "top", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                    exc.exc_type = exc.exc_value = exc.exc_traceback = None
            except Exception as e:
                exc.exc_type = type(e).__name__
                exc.exc_value = str(e)
                exc.exc_traceback = str(e.__traceback__)
                await log_chat(user_id, update.message.chat.username, "top", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
                await update.message.reply_text("Something went wrong, please contact support or try again later.")

    else:
        log_tamago(update, response='To use this function please use /renew to get a subscription')
        await update.message.reply_text('To use this function plase use /renew to get a subscription' , parse_mode='MarkdownV2')

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

            #print (message)
            try: 
                for parts in message:
                
                    if parts == message[0]:
                        await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=wait_message.message_id,
                        text=parts
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    else:
                        await update.message.reply_text(parts , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    await log_chat(user_id, update.message.chat.username, "avg", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                    exc.exc_type = exc.exc_value = exc.exc_traceback = None
            except Exception as e:
                    exc.exc_type = type(e).__name__
                    exc.exc_value = str(e)
                    exc.exc_traceback = str(e.__traceback__)
                    await log_chat(user_id, update.message.chat.username, "avg", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                    exc.exc_type = exc.exc_value = exc.exc_traceback = None                       
                    await update.message.reply_text("Something went wrong, please contact support or try again later.")

    else:
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')

async def get_top_holders_and_formulate_x_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id 
    if check_access(user_id):
        if len(context.args) != 1:
            await update.message.reply_text("Please send me a token address.")
            context.user_data['awaiting_token_address'] = True
            context.user_data['formulate_x_post_started'] = True 
            return 
        else:
            token_address = context.args[0]
            wait_message = await update.message.reply_text("Munki is scratching his butt, please wait...")
            time_now = float(time.time())

            async def custom_log(message):
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=wait_message.message_id,
                    text=escape_markdown(message)
                , parse_mode='MarkdownV2', disable_web_page_preview=True)

            message = await process_ca_and_post_to_x(token_address, limit, log_to_client=custom_log)
            # message = ['36 whales have aped $DOGE state. The current MC is $1267.2m, barking mad gains soon!.\n\n Munki', '50 whales have aped $SafeMoon. The current MC is $8212.4m, safely mooning soon!.\n\n Munki']

            log_message = 'n/a'
            if type(message) == str:
                log_message = message
            elif message and len(message) > 0:
                log_message = message[0]

            if message == None or len(message) == 0:
                await log_chat(user_id, update.message.chat.username, "ca", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                await update.message.reply_text("No bananas found, this ca is boring, try another?")
                return

            try: 
                for parts in message:
                
                    if parts == message[0]:
                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=wait_message.message_id,
                            text=escape_markdown(parts)
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    else:
                        await update.message.reply_text(escape_markdown(parts) , parse_mode='MarkdownV2', disable_web_page_preview=True)
                    await log_chat(user_id, update.message.chat.username, "ca", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                    exc.exc_type = exc.exc_value = exc.exc_traceback = None
            except Exception as e:
                    exc.exc_type = type(e).__name__
                    exc.exc_value = str(e)
                    exc.exc_traceback = str(e.__traceback__)
                    await log_chat(user_id, update.message.chat.username, "ca", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                    exc.exc_type = exc.exc_value = exc.exc_traceback = None                       
                    await update.message.reply_text("Something went wrong, please contact support or try again later.")

    else:
        await update.message.reply_text('Pssssst. Only for the boss\' eyes.' , parse_mode='MarkdownV2')

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
            wait_message = await update.message.reply_text("Analyzing token and looking for Whales, please chill...")
            message = await top_holders_net_worth_map(token_address, limit )
            if type(message) == str:
                log_message = message
            else:
                log_message = message[0]

            try:
                log_tamago(update, response=message)
                await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=wait_message.message_id,
                        text=message
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                await log_chat(user_id, update.message.chat.username, "map", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                #print (message)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
            except Exception as e:
                exc.exc_type = type(e).__name__
                exc.exc_value = str(e)
                exc.exc_traceback = str(e.__traceback__)
                await log_chat(user_id, update.message.chat.username, "map", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
                await update.message.reply_text("Something went wrong, please contact support or try again later.")


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
            try:
                await update.message.reply_text(holder_message , parse_mode='MarkdownV2', disable_web_page_preview=True)
                await log_chat(user_id, update.message.chat.username, "dist", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
            #print (holder_message)
            except Exception as e:
                exc.exc_type = type(e).__name__
                exc.exc_value = str(e)
                exc.exc_traceback = str(e.__traceback__)
                await log_chat(user_id, update.message.chat.username, "dist", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
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
            wait_message = await update.message.reply_text("Looking for Fresh Wallets, please chill...")
            holder_message = await fresh_wallets_v2_parsed(token_address, limit)
            if type(holder_message) == str:
                log_message = holder_message
            else:
                log_message = holder_message[0]
            try:
                await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=wait_message.message_id,
                        text=holder_message
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                await log_chat(user_id, update.message.chat.username, "fresh", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
            except Exception as e:
                exc.exc_type = type(e).__name__
                exc.exc_value = str(e)
                exc.exc_traceback = str(e.__traceback__)
                await log_chat(user_id, update.message.chat.username, "fresh", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
                await update.message.reply_text("Something went wrong, please contact support or try again later.")
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
            try:
                
                
                #print (holder_message)
                log_tamago(update, response=holder_message)
                await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=wait_message.message_id,
                        text=holder_message
                        , parse_mode='MarkdownV2', disable_web_page_preview=True)
                
                await log_chat(user_id, update.message.chat.username, "exp", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None           
            except Exception as e: 
                exc.exc_type = type(e).__name__
                exc.exc_value = str(e)
                exc.exc_traceback = str(e.__traceback__)
                await log_chat(user_id, update.message.chat.username, "exp", token_address,update.message.__str__(),log_message, float(time.time())-time_now, exc_type=exc.exc_type, exc_value=exc.exc_value, exc_traceback=exc.exc_traceback)
                exc.exc_type = exc.exc_value = exc.exc_traceback = None
                await update.message.reply_text("Something went wrong, please contact support or try again later.")   
    else:
        log_tamago(update, response='To use this function please use /renew to get a subscription')
        await update.message.reply_text('To use this function please use /renew to get a subscription' , parse_mode='MarkdownV2')


async def free_trial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    refcode_list = get_refcodes_list()
    info = get_user_info(user_id)



    if (check_access(user_id)):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You have an active subscription expiring {time_left}'
        await update.message.reply_text(f'{response}')

    elif len(context.args) != 1:
            await update.message.reply_text("Please send me a Code.")
            context.user_data['awaiting_refcode'] = True
            return

    elif context.args[0] not in refcode_list:
        await update.message.reply_text("Invalid Referral Code! Please try another one.")
    else:
       response = free_trial(str(user_id), refcode=context.args[0], free_trial=7)
       await update.message.reply_text(f'{response}')
    
async def userid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_tamago(update, response=update.message.chat.id)
    await update.message.reply_text(f'{update.message.chat.id}')


async def renew_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    info = get_user_info(user_id)

    if check_access(user_id):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You already have an active subscription expiring {time_left}'
        log_tamago(update, response=response)
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
        log_tamago(update, response=renew_message)
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
    log_tamago(update, response=response)
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=check_message.message_id,
        text=response)

