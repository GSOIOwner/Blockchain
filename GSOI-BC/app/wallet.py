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