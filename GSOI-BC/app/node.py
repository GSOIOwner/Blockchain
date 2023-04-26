import requests
import json

class Node:
    def __init__(self, uuid, nodeAddress, nodeAPY, numberOfTransactions, amountStaked, stakingIndex, maxTransations,
                  maxAmountStaked):
        self.uuid = uuid
        self.nodeAddress = nodeAddress
        self.nodeAPY = nodeAPY
        self.numberOfTransactions = numberOfTransactions
        self.amountStaked = amountStaked
        self.stakingIndex = stakingIndex
        self.maxTransations = maxTransations
        self.maxAmountStaked = maxAmountStaked

def GetNodeAPY(address):
    ploads = { 'Address': address }
    r = requests.get('https://host.docker.internal:7084/api/SmartContract/GetValidatorAPY', params=ploads, verify=False)
    print ("GetNodeAPY", r.text)
    return r.text

def GetNodeAmountStaked(address):
    ploads = { 'Address': address }
    r = requests.get('https://host.docker.internal:7084/api/SmartContract/GetValidatorStakedAmount', params=ploads, verify=False)
    print ("GetNodeAmountStaked", r.text)
    return r.text
    