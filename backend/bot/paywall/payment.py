from solana.rpc.api import Client
from datetime import datetime, timedelta
from solders.keypair import Keypair
import pandas as pd
from solders.pubkey import Pubkey
import numpy as np
from solders.rpc import responses
from .security import *
from .userdb_handler import *
# Solana RPC endpoint
solana_client = Client("https://api.mainnet-beta.solana.com")   

def check_user(user_id, referal_info):
    df = fetch_user_by_id(str(user_id))

    if str(user_id) == str(df['user_id'][0]):
        has_wallet = df['public_key'][0]
        if pd.notna(has_wallet):  # pd.notna() checks if the value is not NaN
            return has_wallet
    else:
        insert_user(str(user_id), 0, referal_info)
        generate_wallet(str(user_id))
        update_user('joined', psycopg2.extensions.AsIs('CURRENT_TIMESTAMP'), str(user_id))
        

def generate_wallet(user_id):

    public_key, private_key = create_keypair()
    update_user( "public_key", str(public_key), str(user_id))


    update_user( "private_key", str(private_key), str(user_id))

    
def check_balance(wallet_address):
    try:
        # Convert the string address to a PublicKey object
        public_key = Pubkey.from_string(wallet_address)
    except ValueError as e:
        print(f"Invalid Solana wallet address. Error: {e}")
        return

    # Get account info
    account_info = solana_client.get_account_info(public_key)
    payed = 0

    if account_info.value is None:
        response = f"Balance for wallet is 0 SOL. Please transfer SOL or wait for transaction to finish and check again"
        return response, payed

    # Get balance in lamports and convert to SOL
    balance_in_lamports = account_info.value.lamports
    balance_in_sol = balance_in_lamports / 10**9  # Convert lamports to SOL

    # Format and send the response
    response = f"Balance for wallet {wallet_address}: {balance_in_sol} SOL "
    if balance_in_sol < 0.01:
        remaining_sol = 0.01 - balance_in_sol 
        response = response  + f'Please transfer {remaining_sol} SOL and check again to unlock features'
        return response, payed 
    
    else:
        response = 'Happy Trading! the features are now unlocked'
        payed = 1
        # Store this in a database or cache system
        return response, payed
    
def get_user_info( user_id):
    user_id = str(user_id)
    df = fetch_user_by_id(user_id)
    df = df.set_index('user_id')

    row_as_dict = df.loc[user_id].to_dict()
    row_as_dict ["user_id"] = user_id
    return row_as_dict

# Grant access 
def grant_access( user_id):
    info = get_user_info( user_id)
    wallet_address = info['public_key']
    if (check_access(user_id)):
        time_left = datetime.strptime( info['expiration_date'],"%Y-%m-%d %H:%M:%S.%f")
        time_left=time_left.strftime("%B %d, %Y %I:%M%p %Z")
        response = f'You have an active subscription expiring {time_left}'
        return response

    else:
        response, payed = check_balance(wallet_address) 
       
        if payed == 1:
            expiration_date = datetime.now() + timedelta(days=30)
            # Store this in a database or cache system
            update_user ('expiration_date', expiration_date, user_id)

            if info['referred_by'] is None: 
        
                referee_id = info['referred_by']
                ref_info = get_user_info(referee_id)
                referrals = int(ref_info['referrals']) + 1
                update_user('referrals', referrals, referee_id)
                return response

            else:
                return response
        else:
            return response



def check_access(user_id):
    user_info =  get_user_info(str(user_id))
    
    expiration_date = user_info['expiration_date']
    if pd.isna(expiration_date):
        return False
    else :
        return pd.to_datetime(expiration_date) > datetime.now()


def deposit_wallet(user_id, deposit_wallet):
    update_user('deposit_wallet', deposit_wallet, str(user_id))
    return f'Reward wallet updated to: \n {deposit_wallet}' 

 

