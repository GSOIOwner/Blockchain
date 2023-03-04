from cmd import PROMPT
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from kafka import KafkaConsumer
import uvicorn 
import blockchain
import uuid
import threading
import json 
import wallet
import transaction
import transactionPool
import cryptoHash
import kafkaPublisher
import validator
import time
import random

app = FastAPI()

CurrentBlockchain = blockchain.Blockchain()
blockchainOwner = wallet.initialize_wallet()
Wallet = wallet.initialize_wallet()

#print ("Wallet", Wallet.publicKey)
currentTransacionPool = transactionPool.TransactionPool()

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
    kafkaPublisher.publishKafkaValidatorNotVerified(newValidator)

    return data

def thread_verifyValidators():
    ## De 5 em 5 minutos vamos verificar os validadores
    while(True):
        time.sleep(10)
        consumer = KafkaConsumer('updateValidatorNotVerified', 
         auto_offset_reset='earliest', consumer_timeout_ms=5000)
        
        #print('After consumer updateValidatorNotVerified', flush=True)
        for message in consumer:
            validatorFromJson = json.loads(message.value)
            convertedValidator = validator.Validator(validatorFromJson['Address'], validatorFromJson['amount'])
            
            hasTransactionForV = hasTransactionForValidator(convertedValidator)
            if(hasTransactionForV == True):
                isValidatorAlreadyV = isValidatorAlreadyVerified(convertedValidator)
                if(isValidatorAlreadyV == False):
                    convertedValidator.isVerified = True   
                    kafkaPublisher.publishKafkaValidatorVerified(convertedValidator)
                         
def hasTransactionForValidator(validator):
    for block in CurrentBlockchain.chain:
            for transaction in block.transactions:
                if(transaction.toAddress == "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw=" 
                and transaction.fromAddress == validator.Address):
                    return True

    return False

def isValidatorAlreadyVerified(validatorToVerify):
    consumer = KafkaConsumer('updateValidatorVerified', auto_offset_reset='earliest',
     consumer_timeout_ms=5000)
    
    for message in consumer:
        validatorVerified = json.loads(message.value)
        convertedVerifiedValidator = validator.Validator(validatorVerified['Address'],
         validatorVerified['amount'])

        if(convertedVerifiedValidator.Address == validatorToVerify.Address):
            return True

    return False

x = threading.Thread(target=thread_verifyValidators, args=(), daemon=True)
x.start()

def thread_chooseValidators():
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
    
    

y = threading.Thread(target=thread_chooseValidators, args=(), daemon=True)
y.start()


# def thread_subscriber():
#     print("Thread stared")
#     consumer = KafkaConsumer('updateNodes3', group_id='204', auto_offset_reset='earliest')
#     for msg in consumer:
#         block = json.loads(msg.value)
#         convertedTransaction = transaction.Transaction(block['fromAddress'], block['toAddress'],
#          block['amount'], block['timestamp'], block['originNode'], block['hydrogen'],
#          block['units'], block['workTime'], block['upTime'])
#         #print("ConvertedBLock", convertedBLock.__dict__)
#         currentTransacionPool.addTransaction(convertedTransaction)

# x = threading.Thread(target=thread_subscriber, args=(), daemon=True)
# x.start()

def init():
    convertedValidator = validator.Validator(
        "p5rZosydTkViWz9iGjs9lO+wGbly2f0VeoD09ReaqOw="
        ,1000.0
        ,True
        ) 
    kafkaPublisher.publishKafkaValidatorVerified(convertedValidator)

init()

if __name__ == "__main__":
    uvicorn.run(app, port=5000, host="127.0.0.1")

# @app.post("/block")
# def read_root(data: Transaction):
#     newBlockData = Data(data.fromAddress, data.toAddress, data.amount, data.timestamp, data.originNode, data.hydrogen, data.units, data.workTime, data.upTime)
#     #print(newBlockData.__dict__)
#     CurrentBlockchain.addBlock(newBlockData)
#     return RedirectResponse("/blocks", status_code=303)