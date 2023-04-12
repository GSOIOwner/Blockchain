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

        hashed_string = hashlib.sha256(
            transactionToString.encode('utf-8')
            ).hexdigest()

        return hashed_string

    def isValidBlock(chain, transactions, hash):
        if transactions is not None and hash != chain[len(chain)-1].hash:
                return True

    def toJson(self):
        newBlockToJson = { 
                'timestamp' : str(self.timestamp),
                 'lastHash' : self.lastHash,
                 'hash' : self.hash,
                 'transactions' : [obj.__dict__ for obj in self.transactions]
                 }
        return newBlockToJson

    def getGenesis():
        ownerAddress = wallet.getOwnerAddress()
        newMsg = cryptoHash.CryptoHash.joinTransaction(ownerAddress,
         ownerAddress,
         369369369)

        signature = wallet.Owner.sign(newMsg, ownerAddress)

        newTransaction = transaction.Transaction(fromAddress="start",
        toAddress = ownerAddress, amount = 369369369,
        signature = signature, isStake=True)

        firstBlock = Block(datetime.now(), "lastHash", "hash-one", [newTransaction])
        
        list_firstBlock_Json=[firstBlock.toJson()]
        f=open("dummy_chain.txt", "ab")
        data = json.dumps(list_firstBlock_Json)
        f.write(data.encode("utf-8") + "\n".encode("utf-8"))
        
        return firstBlock
