import json
import socket
import sys
import threading
import os
import time
import random

# TODO:
# This is all going down the hole.
# Em homenagem eu renomeava esta classe para outra coisa mas deixava aqui um comentário RIP KAFKA.
# Apagar tudo o que é de Kafka e criar sistema de sincronização com Client/Server TCP

# RIP KAFKA

# environment_IP=os.getenv('IP')
# environment_OP=os.getenv('Port')

# rendezvous = (environment_IP, int(environment_OP)) #ip local do servidor,para usar o externo temos de fazer router stuff

class peer_synchronizer:
  def __init__(self,IP="0.0.0.0",PORT=0):
    self.rendezvous=(IP,int(PORT))
  
  def connect_socket(self,IP='0.0.0.0',PORT=0):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((IP, PORT))

  def socker_server_creation(self,IP,PORT):
    self.sock=socket.create_server((IP,PORT),family=socket.AF_INET,reuse_port=True) #nao funciona no windows, para funcionar retirar o reuse_port=true, e mudar o porto para cada servidor!

  def Save_IP(self):
    self.connect_socket()
    MyIP = os.getenv('IP')
    myPort = os.getenv('API_PORT')
    clientIP = MyIP+":"+myPort
    # -> client de testes, usar este para dar save do IP
    self.sock.connect(self.rendezvous)
    self.sock.send(b'Save_IP')
    time.sleep(0.5)
    self.sock.send(clientIP.encode('utf-8'))
    self.sock.close()
    
  def Download_IP(self):
    self.connect_socket()
    self.sock.connect(self.rendezvous)
    self.sock.send(b'Download_IP')
    file = "IPs.txt"
    f=open(file, "wb")
    data = self.sock.recv(1024)
    f.write(data)
    print(data, flush=True)
    self.sock.close()
  
  def Download_blockchain(self):
    self.connect_socket()
    lines = open('IPs.txt').read().splitlines()
    myline =random.choice(lines)
    self.sock.connect((myline.split(":")[0],9000))
    self.sock.send(b'Send') #TODO: enviar que parte da blockchain vamos querer receber
    msg=self.sock.recv(1024)
    f=open("dummy_chain.txt",'wb')
    f.write(msg)
    self.sock.send(b'Chain received')
    self.sock.close()

  def Send_last_block(self,IP,PORT):
    self.connect_socket()
    self.sock.connect((IP,9000))
    self.sock.send(b'Update')
    time.sleep(1)
    f=open('dummy_chain.txt','rb')
    dummy_chain= json.load(f)
    data=dummy_chain[-1]
    self.sock.send(json.dumps(data).encode("utf-8"))
    self.sock.close()
