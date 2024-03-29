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

    def clear(self):
        self.transaction_pool.clear()

    def getTransactionForValidator(self, address):
        nodeAddress = "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw="
        
        if(len(self.transaction_pool) != 0):
            newMsg = cryptoHash.CryptoHash.joinTransaction(nodeAddress,
             address, 50)

            signature = wallet.Owner.sign(newMsg, nodeAddress)

            newTransaction = transaction.Transaction(fromAddress = nodeAddress,
            toAddress = address, amount = 50, signature = signature)
            
            return newTransaction

    def checkValidTransactions(self, address):
        validTransactions = []
        for transaction in self.transaction_pool:
            msg = cryptoHash.CryptoHash.joinTransaction(transaction.fromAddress, transaction.toAddress,
                             transaction.amount)
            
            result = wallet.validate_signature(transaction.fromAddress, msg, transaction.signature)
            
            if result is True:
                validTransactions.append(transaction)
        
        validatorTransaction = self.getTransactionForValidator(address)
        validTransactions.append(validatorTransaction)
        
        return validTransactions  

    def validateTransactions(self, chain, address):
        vTransactions = self.checkValidTransactions(address)
        chain.addBlock(vTransactions)
        self.transaction_pool = []

    


      