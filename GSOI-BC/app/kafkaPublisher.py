from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092')

# TODO:
# This is all going down the hole.
# Em homenagem eu renomeava esta classe para outra coisa mas deixava aqui um comentário RIP KAFKA.
# Apagar tudo o que é de Kafka e criar sistema de sincronização com Client/Server TCP

def publishKafkaBlock(newBlock):
        producer.send('updateNodes3', json.dumps(newBlock.toJson()).encode('utf-8'))

def publishKafkaValidatorNotVerified(newValidator):
        producer.send('updateValidatorNotVerified', json.dumps(newValidator.__dict__).encode('utf-8'))

def publishKafkaValidatorVerified(newValidator):
        #print(newValidator.__dict__)
        producer.send('updateValidatorVerified', json.dumps(newValidator.__dict__).encode('utf-8'))