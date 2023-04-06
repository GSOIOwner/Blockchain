from cmd import PROMPT
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import uvicorn 
import blockchain
import uuid
import threading
import json 
import wallet
import transaction
from transaction import Transaction
import transactionPool
import cryptoHash
import peer_synchronizer
import validator
import time
import random
import socket
import os
import requests
from typing import List

app = FastAPI(openapi_schema={"openapi": "3.0.0", "arbitrary_types_allowed": True})

max_socket=65000
CurrentBlockchain = blockchain.Blockchain()
currentTransacionPool = transactionPool.TransactionPool()

nodeAddress = os.getenv('nodeAddress')
ownerAddress = wallet.getOwnerAddress()

class TransactionFastAPI(BaseModel):
    fromAddress : str 
    toAddress : str
    amount : float
    timestamp: str = None
    originNode: str = None
    hydrogen: float = None
    units: str = None
    workTime : float = None# in hours
    upTime : str = None
    signature: str 
    
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
     data.hydrogen, data.units, data.workTime, data.upTime, signature)

    currentTransacionPool.addTransaction(newTransaction)
    return RedirectResponse("/transactionPool", status_code=303)

@app.get("/transactionPool")
def read_root():
    return currentTransacionPool.getTransactionPool()

@app.get("/wallet-info")
def read_root(address: str):
    hasConductedTransaction = False
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

# TODO:   
# Este metodo desaparece, penso que pode é ser criado, como dito no Transaction.py, uma variavel no Transaction "BecomingValidator" para identificar que foi uma transação usada para se tornar validator/(nó).
# Ficamos apenas assim com o método /transact

@app.post("/becomeValidator")
def read_root(data: ValidatorFastAPI):
    # Entra na lista de validadores

    # Criar metodo na middleware que devolve o owner address
    newMsg = cryptoHash.CryptoHash.joinTransaction(data.address,
     "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=",
     data.amount)

    signature = wallet.Owner.sign(newMsg, data.address)

    newTransaction = transaction.Transaction(  fromAddress= data.address,
    toAddress= "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=",
    amount= data.amount,
    signature= signature)

    currentTransacionPool.addTransaction(newTransaction)

    ## Criar um objecto de validadores
    newValidator = validator.Validator(data.address, data.amount)

    ## Adicionar esse objecto a uma lista de validadores
    #kafkaPublisher.publishKafkaValidatorNotVerified(newValidator)

    return data

# POST method to receive and update transaction pool
@app.post('/api/transaction_pool')
async def receiveTransactionPool(payload: TransactionPoolPayload):
    print('Received Transaction Pool: ', payload.transaction_pool)
    new_transaction_pool = []

    # Loop through each transaction in the payload and create a new Transaction object
    for transaction_data in payload.transaction_pool:
        transaction_dict = transaction_data.dict()
        new_transaction = transaction.Transaction(**transaction_dict)
        new_transaction_pool.append(new_transaction)

    # Update the transaction pool with the new transactions
    currentTransactionPool = transactionPool.TransactionPool(new_transaction_pool)

    # Verify the authenticity of the payload by checking the address
    # ...

    print('Going to validate Transactions')
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



#y = threading.Thread(target=thread_chooseValidators, args=(), daemon=True)
#y.start()

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
            print(msg)
            f=open("dummy_chain.txt")
            dummy_blockchain= json.load(f) # TODO: fazer a comparação do que recebemos com o que ja esta na chain, ver o codigo do jess
            print(dummy_blockchain)
            f.write(msg)
            f.close()
            conn.close()


def thread_choose_validator(): #TODO: complete i
    print('Insine thread_choose_validator...', flush=True)

    while True:
        print('Insine thread_choose_validator...', flush=True)
        if(len(currentTransacionPool.transaction_pool) > 0):
            lines = open('IPs.txt').read().splitlines()
            myline =random.choice(lines)
            print('Choosen IP: ', myline, flush=True)
            transaction_pool = currentTransacionPool.to_dict()
            print(transaction_pool, flush=True)
            headers = {'Content-Type': 'application/json'}
            r = requests.post(f'http://{myline}/api/transaction_pool', data=json.dumps(transaction_pool), headers=headers)
            return r.status_code == 200

        time.sleep(20)

# TODO: Retirar Kafka, acho que isto até foi aqui posto só para termos logo um nó validador desde o inicio, que irá morrer
def init():
    peer=peer_synchronizer.peer_synchronizer(os.getenv('IP'),os.getenv('Port'))
    peer.Save_IP()
    time.sleep(5)
    peer.Download_IP()

    #peer.Download_blockchain()
    y = threading.Thread(target=thread_send_blockchain_peers, args=(), daemon=True)
    y.start()

    z = threading.Thread(target=thread_choose_validator, args=(), daemon=True)
    z.start()
    #Get Owner Wallet Address
    #Get Own Wallet Address
    
init()

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv('API_PORT')), host='0.0.0.0')
