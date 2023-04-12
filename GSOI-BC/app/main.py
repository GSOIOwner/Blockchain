from cmd import PROMPT
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import uvicorn 
import uuid
import threading
import json 

import time
import random
import socket
import os
import requests
import blockchain
import block
import node
import wallet
import transaction
from transaction import Transaction
import transactionPool
import cryptoHash
import peer_synchronizer

app = FastAPI(openapi_schema={"openapi": "3.0.0", "arbitrary_types_allowed": True})


max_socket = 65000
CurrentBlockchain = blockchain.Blockchain()
currentTransacionPool = transactionPool.TransactionPool()

nodeAddress = os.getenv('nodeAddress')
nodeAPY = os.getenv('nodeAPY')
nodeAmountStaked = os.getenv('nodeAmountStaked')

currentNode = node.Node(nodeAddress, nodeAPY, 0, nodeAmountStaked)

ownerAddress = wallet.getOwnerAddress()

class TransactionFastAPI(BaseModel):
    fromAddress : str 
    toAddress : str
    amount : float
    timestamp: str = None
    originNode: str = None
    hydrogen: float = None
    units: str = None
    workTime : float = None
    upTime : str = None
    signature: str 
    isStake : bool = False
    
class ValidatorFastAPI(BaseModel):
    address : str
    amount : float

class WalletBalance(BaseModel):
    address : str

class TransactionPoolPayload(BaseModel):
    transaction_pool: List[TransactionFastAPI]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/getNode")
def read_root():
    return uuid.getnode()

@app.get("/blocks")
def read_root():
    return CurrentBlockchain.chain

@app.post("/transact")
def read_root(data: TransactionFastAPI):
    newMsg = cryptoHash.CryptoHash.joinTransaction(data.fromAddress, data.toAddress,
     data.amount)

    signature = wallet.Owner.sign(newMsg, data.fromAddress)

    newTransaction = transaction.Transaction(data.fromAddress, data.toAddress,
     data.amount, data.timestamp, data.originNode, 
     data.hydrogen, data.units, data.workTime, data.upTime, signature, data.isStake)

    currentTransacionPool.addTransaction(newTransaction)
    return RedirectResponse("/transactionPool", status_code=303)

@app.get("/transactionPool")
def read_root():
    return currentTransacionPool.getTransactionPool()

@app.get("/wallet-info")
def read_root(address: str):
    
    outputsTotal = 0

    for block in CurrentBlockchain.chain:
        for transaction in block.transactions:
            if(transaction.fromAddress == address):
                outputsTotal = outputsTotal - transaction.amount

            if(transaction.toAddress == address):
                outputsTotal = outputsTotal + transaction.amount  
    
    json = {
        "Address": address,
        "Balance": outputsTotal
    }

    return json

@app.post('/api/transaction_pool')
async def receiveTransactionPool(payload: TransactionPoolPayload):
    new_transaction_pool = []

    for transaction_data in payload.transaction_pool:
        transaction_dict = transaction_data.dict()
        new_transaction = transaction.Transaction(**transaction_dict)
        new_transaction_pool.append(new_transaction)

    currentTransactionPool = transactionPool.TransactionPool(new_transaction_pool)

    currentTransactionPool.validateTransactions(CurrentBlockchain, nodeAddress)

    return {'message': 'Transaction pool updated successfully'}

@app.get("/Save_IP")
def read_root():
    peer=peer_synchronizer.peer_synchronizer(os.getenv('IP'),os.getenv('Port'))
    peer.Save_IP()
    #idk se queres imprimir aqui algo tipo "done"
    return 

@app.get("/Download_IP")
def read_root():
    peer=peer_synchronizer.peer_synchronizer(os.getenv('IP'),os.getenv('Port'))
    peer.Download_IP()
    return 

@app.get("/Get_chain")
def read_root():
    peer=peer_synchronizer.peer_synchronizer(os.getenv('IP'),os.getenv('Port'))
    peer.Download_blockchain()
    file=open('dummy_chain.txt',"r")
    data=file.read()
    return data

@app.get("/send_last_block")
def read_root():
        peer=peer_synchronizer.peer_synchronizer()
        peer.Send_last_block(os.getenv('IP'),9000)
        return 

@app.post("/set_staking_percentage")
def read_root(address: str, staking_percentage : int):
    
    if address == nodeAddress:
        CurrentStakingPercentage = staking_percentage

    
    return json

def thread_send_blockchain_peers():
    server=peer_synchronizer.peer_synchronizer() 
    server.socker_server_creation(socket.gethostbyname(socket.gethostname()),9000)
    server.sock.listen()
    while True:
        conn, address = server.sock.accept()
        data=conn.recv(1024)
        print(data)
        if data==b'Send': # TODO: falta comprimir o ficheiro 
            f=open("dummy_chain.txt","rb")
            data=f.read()
            print(data)
            conn.send(data)
            msg=conn.recv(1024)
            print(msg)
            f.close
            conn.close()
        if data==b'Update':
            msg=conn.recv(max_socket)
            f=open("dummy_chain.txt",'rb')
            f.close()
                       
            msg = json.loads(msg.decode("utf-8"))
            timestamp = msg['timestamp']
            lastHash = msg['lastHash']
            hash = msg['hash']
            transactions_data = msg['transactions']

            transactions = []
            for transaction_data in transactions_data:
                data_transaction = transaction.Transaction(**transaction_data)
                transactions.append(data_transaction)
                
            block_msg = block.Block(timestamp, lastHash, hash, transactions)
            CurrentBlockchain.sync_block(block_msg)
            conn.close()

def thread_choose_validator(): 
    while True:
        if(len(currentTransacionPool.transaction_pool) > 0):
            lines = open('IPs.txt').read().splitlines()
            myline =random.choice(lines)
            transaction_pool = currentTransacionPool.to_dict()
            headers = {'Content-Type': 'application/json'}
            r = requests.post(f'http://{myline}/api/transaction_pool', data=json.dumps(transaction_pool), headers=headers)
            return r.status_code == 200

        time.sleep(20)

def init():
    peer=peer_synchronizer.peer_synchronizer(os.getenv('IP'),os.getenv('Port'))
    peer.Save_IP()
    time.sleep(5)
    peer.Download_IP()

    y = threading.Thread(target=thread_send_blockchain_peers, args=(), daemon=True)
    y.start()

    z = threading.Thread(target=thread_choose_validator, args=(), daemon=True)
    z.start()

    #TODO: Get Owner Wallet Address
    #TODO: Get Own Wallet Address
    
    
init()

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv('API_PORT')), host='0.0.0.0')
