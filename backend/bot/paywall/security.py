from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import os

print (os.getcwd())

current_dir = os.path.dirname(os.path.abspath(__file__))
pem_file_path = os.path.join(current_dir, '../public_key.pem')
print (pem_file_path)



with open(pem_file_path, 'r') as file:
    content = file.read()

# with open("public_key.pem", "rb") as key_file:
#     public_key = serialization.load_pem_public_key(
#         key_file.read()
#     )

# Function to encrypt wallet private key
def encrypt_private_key(wallet_private_key, public_key):
    # Assuming wallet_private_key is in bytes form
    encrypted = public_key.encrypt(
        wallet_private_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted
def create_keypair():
    
    keypair = Keypair()  # Ensure Keypair is imported and defined
    raw = bytes(keypair)
    public_key = keypair.pubkey()

    assert keypair.pubkey() == public_key
    assert Pubkey.from_string(str(public_key)).is_on_curve()
    
    with open("public_key.pem", "rb") as key_file:
        encryption_key = serialization.load_pem_public_key(
            key_file.read()
        )
    
    private_key = encrypt_private_key(raw, encryption_key)
    
    return public_key, private_key

