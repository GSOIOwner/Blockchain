
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