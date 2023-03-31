import binascii
import requests

class Owner:
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