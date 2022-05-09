from ..Agent import Agent, StateChange
from ..Role import Role, RoleType
from ..Common import Transaction, Block


class BlockchainMaintainerStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        self.txpool = {}


class BlockchainMaintainer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER)

    @staticmethod
    def state_change() -> StateChange:
        return BlockchainMaintainerStateChange()

    @staticmethod
    def validate_transaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Validate a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def validate_block(agent: Agent, block: Block, *args, **kwargs) -> bool:
        """ Validate a specific Block

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def store_transaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Store a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def append_block(agent: Agent, block: Block, *args, **kwargs) -> bool:
        """ Append a specific block to the local blockchain

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def execute_transaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        raise NotImplementedError
