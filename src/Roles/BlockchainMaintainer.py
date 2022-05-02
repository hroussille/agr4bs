from Role import Role, RoleType
from Common import Transaction, Block


class BlockchainMaintainer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER)
        self._txPool = {}
        self._blockchain = {}

    @property
    def txPool(self):
        return self._txPool

    @txPool.setter
    def txPool(self, newTxPool):
        self._txPool = newTxPool

    @txPool.deleter
    def txPool(self):
        del self._txPool

    @property
    def blockchain(self):
        return self._blockchain

    @blockchain.setter
    def blockchain(self, newBlockchain):
        self._blockchain = newBlockchain

    @blockchain.deleter
    def blockchain(self):
        del self._blockchain

    def validateTransaction(self, transaction: Transaction, *args, **kwargs) -> bool:
        """ Validate a specific transactiont

            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    def validateBlock(self, block: Block, *args, **kwargs) -> bool:
        """ Validate a specific Block

            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    def storeTransaction(self, transaction: Transaction, *args, **kwargs) -> bool:
        """ Store a specific transaction

            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """
        raise NotImplementedError

    def appendBlock(self, block: Block, *args, **kwargs) -> bool:
        """ Append a specific block to the local blockchain

            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        raise NotImplementedError

    def executeTransaction(self, transaction: Transaction, *args, **kwargs) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        raise NotImplementedError
