
"""
Abstract implementation of the BlockProposer role as per AGR4BS

BlockProposerContextChange:

The BlockProposerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

BlockProposer:

The BlockProposer implementation which MUST contain the following behaviors :
- select_transaction
- create_block
- propose_block
"""

from ..agents import Agent, ContextChange, AgentType
from .role import Role, RoleType
from ..blockchain import Block, Transaction


class BlockProposerContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (BlockProposer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.transaction_selection_strategy = None


class BlockProposer(Role):

    """
        Implementation of the BlockProposer Role which must
        expose the following behaviors :
        - select_transaction
        - create_block
        - propose_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        role_dependencies = [RoleType.BLOCKCHAIN_MAINTAINER]
        super().__init__(RoleType.BLOCK_PROPOSER, AgentType.EXTERNAL_AGENT, role_dependencies)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockProposerContextChange()

    @staticmethod
    def select_transaction(agent: Agent, transactions: list[Transaction], *args, **kwargs) -> list[Transaction]:
        """ Select a subset of transactions for inclusion in a block

            :param transactions: the available transactions
            :type transactions: list[Transaction]
            :returns: the list of selected transactions
            :rtype: list[Transaction]
        """
        raise NotImplementedError

    @staticmethod
    def create_block(agent: Agent, transactions: list[Transaction], *args, **kwargs) -> Block:
        """ Creates a block with the given transactions

            :param transactions: the transactions to include in the block
            :type transactions: list[Transaction]
            :returns: the block with the transactions included in it
            :rtype: Block
        """

        raise NotImplementedError

    @staticmethod
    def propose_block(block: Block, *args, **kwargs):
        """ Propose a block to the network

            :param block: the block to propose to the network
            :type block: Block
        """
        raise NotImplementedError
