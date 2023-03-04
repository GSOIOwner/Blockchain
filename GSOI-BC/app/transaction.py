import wallet
import json

class Transaction:
    def __init__(self, fromAddress, toAddress, amount, timestamp=None,
     originNode=None, hydrogen=None, units=None, workTime=None, upTime=None, signature=None):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        self.timestamp = timestamp
        self.originNode = originNode
        self.hydrogen = hydrogen
        self.units = units
        self.workTime = workTime
        self.upTime = upTime
        self.signature = signature

