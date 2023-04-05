from hashlib import sha256

class CryptoHash:
    def getHash(fromAddress, toAddress, amount, timestamp, originNode, 
     hydrogen, units, workTime, upTime):
        
        transactionToString = CryptoHash.joinTransaction(fromAddress, toAddress, amount)
        # TRY TO DO A JOIN(' ')
        #print("Hash: " + transactionToString)
        #hashSHA256 = SHA256.new(bytes(transactionToString,'utf-8'))
        hashSHA256 = sha256(transactionToString).hexdigest()
        print("hashSHA256: " + str(hashSHA256))
        
        return hashSHA256

    def joinTransaction(fromAddress, toAddress, amount):
        fromAddressStr = str(fromAddress)
        amountStr = str(amount)
        toAddressStr = str(toAddress)
        
        transactionToString = fromAddressStr + toAddressStr + amountStr 

        return bytes(transactionToString, 'utf-8')