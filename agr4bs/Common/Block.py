class Block(object):

    def __init__(self, creator, transactions) -> None:
        self._transactions = transactions
        self._from = creator
