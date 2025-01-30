from web3 import Web3
import json

# Replace with your EVM L2 RPC URL
RPC_URL = "https://api.developer.coinbase.com/rpc/v1/base/B4XxpVUp3fUUYinP1aZVfNJOCcpQlIgm"

# Connect to the blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    print("Failed to connect to the blockchain")
    exit()

def get_transactions(address, start_block=0, end_block='latest'):
    """
    Fetch all transactions involving the given address.
    """
    transactions = []
    
    if end_block == 'latest':
        end_block = web3.eth.block_number
    print(end_block)
    for block_num in range(start_block, end_block + 1):
        block = web3.get_block(block_num, full_transactions=True)
        
        for tx in block.transactions:
            print("wrf")
            print(block.transactions)
            return
            if tx['from'] == address or tx['to'] == address:
                transactions.append({
                    'block': block_num,
                    'hash': tx.hash.hex(),
                    'from': tx['from'],
                    'to': tx['to'],
                    'value': web3.from_wei(tx['value'], 'ether'),
                    'gas': tx['gas'],
                    'gas_price': web3.from_wei(tx['gasPrice'], 'gwei')
                })
    
    return transactions

if __name__ == "__main__":
    address = "0xa8D189023F544735EC2D5CC41D83AC0410Ffa284"
    
    if not web3.is_address(address):
        print("Invalid Ethereum address")
        exit()
    
    transactions = get_transactions(address)
    
    print(json.dumps(transactions, indent=4))
