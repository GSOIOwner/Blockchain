import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160, SHA256
import base58
import requests

class Owner:
    def __init__(self, private_key: RSA.RsaKey, public_key: bytes, bitcoin_address: bytes):
        self.private_key = private_key
        self.public_key = public_key
        self.bitcoin_address = bitcoin_address

    def sign(msg, address):
            ploads = {'Address': address, 'message': msg}
            r = requests.get('https://localhost:7084/api/Signatures/CreateSignature', params=ploads, verify=False)
            return r.text

def initialize_wallet():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey().export_key()
    hash_1 = calculate_hash(public_key, hash_function="sha256")
    hash_2 = calculate_hash(hash_1, hash_function="ripemd160")
    bitcoin_address = base58.b58encode(hash_2)
    return Owner(private_key, public_key, bitcoin_address)

def calculate_hash(data, hash_function: str = "sha256"):
    if type(data) == str:
        data = bytearray(data, "utf-8")
    if hash_function == "sha256":
        h = SHA256.new()
        h.update(data)
        return h.hexdigest()
    if hash_function == "ripemd160":
        h = RIPEMD160.new()
        h.update(data)
        return h.hexdigest()
        
def validate_signature(Address, message, signature):
    ploads = {'Address': Address, 'message': message, 'signature': signature}
    r = requests.get('https://localhost:7084/api/Signatures/VerifySignature', params=ploads, verify=False)
    if r.text == "true":
        return True
    else:
        return False

def getOwnerAddress():
    r = requests.get('https://localhost:7084/api/SmartContract/GetTokenOwner', verify=False)
    return r.text