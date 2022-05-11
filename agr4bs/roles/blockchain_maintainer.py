"""
Abstract implementation of the BlockchainMaintainer role as per AGR4BS

BlockchainMaintainerStateChange:

The BlockchainMaintainerStateChange exposes changes that need to be made to the
Agent state when the Role is mounted and unmounted.

BlockchainMaintainer:

The BlockchainMaintainer implementation which MUST contain the following behaviors :
- validate_transaction
- validate_block
- store_transaction
- execute_transaction
- append_block
"""

from ..agent import Agent, StateChange
from ..role import Role, RoleType
from ..common import Block, Transaction


class BlockchainMaintainerStateChange(StateChange):
    """
        State changes that need to be made to the Agent when
        the associated Role (BlockchainMaintainer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.txpool = {}


class BlockchainMaintainer(Role):

    """
        Implementation of the BlockchainMaintainer Role which must
        expose the following behaviors :
        - validate_transaction
        - validate_block
        - store_transaction
        - execute_transaction
        - append_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

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
