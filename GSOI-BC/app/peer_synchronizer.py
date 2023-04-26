import json
import socket
import os
import time
import random

class peer_synchronizer:
  def __init__(self,IP="0.0.0.0",PORT=0):
    self.rendezvous=(IP,int(PORT))
  
  def connect_socket(self,IP='0.0.0.0',PORT=0):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((IP, PORT))

  def socker_server_creation(self,IP,PORT):
    self.sock=socket.create_server((IP,PORT),family=socket.AF_INET,reuse_port=True) 

  def Save_IP(self):
    self.connect_socket()
    MyIP = os.getenv('IP')
    myPort = os.getenv('API_PORT')
    nodeAddress = os.getenv('nodeAddress')
    clientIP = MyIP+":"+myPort
    self.sock.connect(self.rendezvous)
    self.sock.send(b'Save_IP')
    time.sleep(3)
    self.sock.send(clientIP.encode('utf-8'))
    time.sleep(3)
    self.sock.send(nodeAddress.encode('utf-8'))
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
    self.sock.send(b'Send') 
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
