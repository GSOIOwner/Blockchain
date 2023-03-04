from datetime import datetime
import hashlib
import json
import transaction
import wallet
import cryptoHash

class Block:
    def __init__(self, timestamp, lastHash, hash, transactions):
        self.timestamp = timestamp
        self.lastHash = lastHash
        self.hash = hash
        self.transactions = transactions

    def createBlock(chain, transactions):
        newBlock = Block(
            timestamp = datetime.now(),
            lastHash = chain[len(chain)-1].hash, 
            hash = Block.getHash(transactions),
            transactions = transactions
            )

        return newBlock

    def getHash(transactions):
        transactionToString = ""
        for transaction in transactions:
            transactionToString += str(transaction.__dict__)

        # TRY TO DO A JOIN(' ')
        hashed_string = hashlib.sha256(
            transactionToString.encode('utf-8')
            ).hexdigest()

        return hashed_string

    def isValidBlock( chain, transactions, hash):
        if transactions is not None and hash != chain[len(chain)-1].hash:
                return True

    def toJson(self):
        newBlockToJson = { 
                'timestamp' : str(self.timestamp),
                 'lastHash' : self.lastHash,
                 'hash' : self.hash,
                 'transactions' : json.dumps([obj.__dict__ for obj in self.transactions])
                 }
        return newBlockToJson

    def getGenesis():
        newMsg = cryptoHash.CryptoHash.joinTransaction("p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=",
         "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=",
         369369369)

        signature = wallet.Owner.sign(newMsg, "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=")

        newTransaction = transaction.Transaction(fromAddress="start",
        toAddress="p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=", amount=369369369,
        signature= signature)

        return Block(datetime.now(), "lastHash", "hash-one", [newTransaction])
