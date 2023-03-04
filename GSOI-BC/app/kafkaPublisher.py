from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def publishKafkaBlock(newBlock):
        producer.send('updateNodes3', json.dumps(newBlock.toJson()).encode('utf-8'))

def publishKafkaValidatorNotVerified(newValidator):
        producer.send('updateValidatorNotVerified', json.dumps(newValidator.__dict__).encode('utf-8'))

def publishKafkaValidatorVerified(newValidator):
        #print(newValidator.__dict__)
        producer.send('updateValidatorVerified', json.dumps(newValidator.__dict__).encode('utf-8'))