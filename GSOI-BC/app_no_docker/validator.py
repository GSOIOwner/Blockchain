# import json

class Validator:
    def __init__(self, Address = None, amount = None, isVerified=None, stakingIndex=None, validatedTransactions=None):
        self.Address = Address
        self.amount = amount
        self.stakingIndex = stakingIndex
        self.isVerified = isVerified
        self.validatedTransactions = validatedTransactions
    # def toJson(self):
    #     return json.dumps(self.__dict__ )
    