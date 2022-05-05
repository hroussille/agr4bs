from ..Agent import Agent
from ..Role import Role, RoleType
from ..Common import Transaction, Block


class BlockchainMaintainer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER)
        self._behaviors = self._behaviors | {
        'validateTransaction': BlockchainMaintainer.validateTransaction,
        'validateBlock': BlockchainMaintainer.validateBlock,
        'storeTransaction': BlockchainMaintainer.storeTransaction,
        'appendBlock': BlockchainMaintainer.appendBlock,
        'executeTransaction': BlockchainMaintainer.executeTransaction
        }

    @staticmethod
    def bind(agent: Agent):
        super(Role, Role).bind(agent)
        setattr(agent, "txpool", {});
        setattr(agent, "blockchain", {});

    @staticmethod
    def unbind(agent: Agent):
        super(Role, Role).unbind(agent);
        delattr(agent, 'txpool');
        delattr(agent, 'blockchain');

    @staticmethod
    def validateTransaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Validate a specific transactiont

            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def validateBlock(agent: Agent, block: Block, *args, **kwargs) -> bool:
        """ Validate a specific Block

            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def storeTransaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Store a specific transaction

            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def appendBlock(agent: Agent, block: Block, *args, **kwargs) -> bool:
        """ Append a specific block to the local blockchain

            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def executeTransaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        raise NotImplementedError
