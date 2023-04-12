class Transaction:
    def __init__(self, fromAddress, toAddress, amount, timestamp=None,
     originNode=None, hydrogen=None, units=None, workTime=None, upTime=None, signature=None, isStake = None):
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
        self.isStake = isStake 

    def to_dict(self):
        return {
            'fromAddress': self.fromAddress,
            'toAddress': self.toAddress,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'originNode': self.originNode,
            'hydrogen' : self.hydrogen,
            'units' : self.units,
            'workTime' : self.workTime,
            'upTime' : self.upTime,
            'signature' : self.signature,
            'isStake' : self.isStake
        }
    