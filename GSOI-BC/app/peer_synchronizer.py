import json
import socket
import sys
import threading
import os
import time

# TODO:
# This is all going down the hole.
# Em homenagem eu renomeava esta classe para outra coisa mas deixava aqui um comentário RIP KAFKA.
# Apagar tudo o que é de Kafka e criar sistema de sincronização com Client/Server TCP

# RIP KAFKA

# environment_IP=os.getenv('IP')
# environment_OP=os.getenv('Port')

# rendezvous = (environment_IP, int(environment_OP)) #ip local do servidor,para usar o externo temos de fazer router stuff

class peer_synchronizer:
  def __init__(self,IP,PORT):
    self.rendezvous=(IP,PORT)
  
  def connect_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind(('0.0.0.0', 0))

  def Save_IP(self):
    self.connect_socket()
    # -> client de testes, usar este para dar save do IP
    self.sock.connect(self.rendezvous)
    self.sock.send(b'Save_IP')
    self.sock.close()
    
  def Download_IP(self):
    self.connect_socket()
    self.sock.connect(self.rendezvous)
    self.sock.send(b'Download_IP')
    file = "IPs"
    f=open(file, "wb")
    data = self.sock.recv(1024)
    f.write(data)
    self.sock.close()