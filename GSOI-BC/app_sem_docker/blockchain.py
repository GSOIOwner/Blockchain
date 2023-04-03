import block 
import hashlib
import json
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = [block.Block.getGenesis()]

    def addBlock(self, transactions):
        newBlock = block.Block.createBlock(self.chain, transactions)
        print(newBlock.__dict__)
        isValidBlock = block.Block.isValidBlock(self.chain, transactions, newBlock.hash)
        print("Was Valid?", isValidBlock)
        
        if isValidBlock:
            self.chain.append(newBlock)
            f=open("dummy_chain.txt", "ab")
            data = newBlock.__dict__
            f.write(data)
    
    # TODO: save blockchain
    

    
    

            



           
