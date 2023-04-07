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
            to_write_dummy_chain=[]
            for blocks in self.chain:
                to_write_dummy_chain.append(blocks.toJson())
            f=open("dummy_chain.txt", "wb")
            data = json.dumps(to_write_dummy_chain)
            f.write(data.encode("utf-8"))
            
    def sync_block(self, block_received):
        isValid=block.Block.isValidBlock(self.chain,block_received.transactions, block_received.hash)
        if isValid:
            self.chain.append(block_received)
            to_write_dummy_chain=[]
            for blocks in self.chain:
                to_write_dummy_chain.append(blocks.toJson())
            f=open("dummy_chain.txt", "wb")
            data = json.dumps(to_write_dummy_chain)
            f.write(data.encode("utf-8"))
        else:
            print("Block already exists!",flush=True)
    # TODO: save blockchain
    

    
    

            



           
