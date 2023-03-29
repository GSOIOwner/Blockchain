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
import transactionPool
import cryptoHash
import peer_synchronizer
import validator
import time
import random
import socket

app = FastAPI()

CurrentBlockchain = blockchain.Blockchain()
currentTransacionPool = transactionPool.TransactionPool()

nodeAddress = "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw="
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

class ValidatorFastAPI(BaseModel):
    address : str
    amount : float

class WalletBalance(BaseModel):
    address : str

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

@app.post("/mine-transactions")
def read_root(address: str):
    # Em vez de minarmos as transações o kafka vai defenir um endereço que esteja em staking para validar a transaçãoç
    currentTransacionPool.validateTransactions(CurrentBlockchain)
    #currentTransacionPool.clear()
    return RedirectResponse("/blocks", status_code=303)

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


# TODO: 
# Necessário ir buscar ao ficheiro a lista de validadores (nós)
# Necessário adaptar o algoritmo, embora esteja um bom algoritmo pensando agora a longo prazo, vai ser dificil com milhões de transações escolher um validator, podemos pensar num "index" mas mais simples.
# Necessário chamar esse validator para validar os blocos na pool atuais

"""def thread_chooseValidators():
    ## De 5 em 5 minutos vamos escolher um validator
    validators = []
    maxStakingAmount = 0
    while(True):
        time.sleep(20)
    ## Buscar ao topico todos os verificados
        consumer = KafkaConsumer('updateValidatorVerified', auto_offset_reset='earliest',
        consumer_timeout_ms=5000)
    
    ## Obter todos os validadores eligiveis e o max staking amount
        for message in consumer:
            validatorFromJson = json.loads(message.value)
            convertedValidator = validator.Validator(validatorFromJson['Address'], validatorFromJson['amount'],
             validatorFromJson['isVerified'], validatorFromJson['stakingIndex'], validatorFromJson['validatedTransactions'])

            if(convertedValidator not in validators):
                validators.append(convertedValidator)
                maxStakingAmount += convertedValidator.amount

    ## Calcular o Staking Index
        maxTransactions = 0
        for block in CurrentBlockchain.chain:
            for transaction in block.transactions:
                maxTransactions += 1

        for validatorToCalculate in validators:
            percentageTransactions = 0
            percentageAmount = validatorToCalculate.amount / maxStakingAmount
            
            if(validatorToCalculate.validatedTransactions is not None):
                percentageTransactions = validatorToCalculate.validatedTransactions / maxTransactions
                
            validatorToCalculate.stakingIndex = percentageAmount - percentageTransactions
    
    ## Escolher validador
        validValidators = None
        highestStakingIndex = 0
        for validValidator in validators:
            if(validValidator.stakingIndex >= highestStakingIndex):
                validValidators = validValidator 
                highestStakingIndex = validValidator.stakingIndex
        
        if(validValidators is None):
            validValidators = random.choice(validators)

    ## Validar transacoes 
        print("Choosen Validator", validValidators.__dict__, flush= True)
        if(currentTransacionPool.transaction_pool is not None and 
         len(currentTransacionPool.transaction_pool) != 0):
            currentTransacionPool.validateTransactions(CurrentBlockchain, validValidators.Address)
    ########## Confirmar o Validador ############
    
    """

#y = threading.Thread(target=thread_chooseValidators, args=(), daemon=True)
#y.start()

def thread_send_blockchain_peers():
    server=peer_synchronizer.peer_synchronizer("192.168.1.53",1234) #o metodo init nao devia de ser assim
    server.connect_socket(socket.gethostbyname(socket.gethostname()),9000)
    print(server.sock.listen())
    while True:
        conn, address = server.sock.accept()
        data=conn.recv(1024)
        print(data)
        if data==b'Send': # falta comprimir o ficheiro 
            f=open("dummy_chain.txt","rb")
            data=f.read()
            print(data)
            conn.send(data)
            msg=conn.recv(1024)
            print(msg)
            f.close
            conn.close()


# TODO: Retirar Kafka, acho que isto até foi aqui posto só para termos logo um nó validador desde o inicio, que irá morrer
def init():
    peer=peer_synchronizer.peer_synchronizer("192.168.1.53",1234)
    #peer.Save_IP()
    #time.sleep(10)
    #peer.Download_IP()
    peer.Download_blockchain()
    """
    y = threading.Thread(target=thread_send_blockchain_peers, args=(), daemon=True)
    y.start()
    while True:
       time.sleep(1)
    """

    #Get Owner Wallet Address
    #Get Own Wallet Address
    
init()

if __name__ == "__main__":
    uvicorn.run(app, port=5000, host="127.0.0.1")

# @app.post("/block")
# def read_root(data: Transaction):
#     newBlockData = Data(data.fromAddress, data.toAddress, data.amount, data.timestamp, data.originNode, data.hydrogen, data.units, data.workTime, data.upTime)
#     #print(newBlockData.__dict__)
#     CurrentBlockchain.addBlock(newBlockData)
#     return RedirectResponse("/blocks", status_code=303)