import wallet
import cryptoHash
import transaction

class TransactionPool:
    def __init__(self, transaction_pool = []):
        self.transaction_pool = transaction_pool

    def getTransactionPool(self):
        return self.transaction_pool

    def addTransaction(self, transaction):
        self.transaction_pool.append(transaction)
    
    def to_dict(self):
        return {'transaction_pool': [transaction.to_dict() for transaction in self.transaction_pool]}
    
    def clear(self):
        self.transaction_pool.clear()

    def getTransactionForValidator(self, address, reward):

        if(len(self.transaction_pool) != 0):
            ownerAddress = wallet.getOwnerAddress()
            newMsg = cryptoHash.CryptoHash.joinTransaction(ownerAddress,
             address, reward)

            signature = wallet.Owner.sign(newMsg, address)

            newTransaction = transaction.Transaction(fromAddress = ownerAddress,
            toAddress = address, amount = reward, signature = signature, isStake=False)
            
            return newTransaction

    def checkValidTransactions(self, address, reward):
        print("Inside check valid transactions", flush=True)
        validTransactions = []
        for transaction in self.transaction_pool:
            msg = cryptoHash.CryptoHash.joinTransaction(transaction.fromAddress, transaction.toAddress,
                             transaction.amount)
            result = wallet.validate_signature(transaction.fromAddress, msg, transaction.signature)

            if result is True:
                print("Valid Transaction", flush=True)
                validTransactions.append(transaction)
        
        validatorTransaction = self.getTransactionForValidator(address, reward)
        print("Got transaction for validator", flush=True)
        validTransactions.append(validatorTransaction)
        
        return validTransactions  

    def validateTransactions(self, chain, address, reward):
        vTransactions = self.checkValidTransactions(address, reward)
        chain.addBlock(vTransactions)
        self.transaction_pool = []
        return vTransactions


    


      