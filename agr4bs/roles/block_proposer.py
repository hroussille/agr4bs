
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


from ..agents import ExternalAgent, ContextChange, AgentType
from ..events import CREATE_BLOCK
from ..network.messages import DiffuseBlock
from .role import Role, RoleType
from ..blockchain import Block, Transaction
from ..common import on, export


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
    @export
    def select_transaction(agent: ExternalAgent, transactions: list[Transaction]) -> list[Transaction]:
        """ Select a subset of transactions for inclusion in a block

            :param transactions: the available transactions
            :type transactions: list[Transaction]
            :returns: the list of selected transactions
            :rtype: list[Transaction]
        """
        return []

    @staticmethod
    @export
    @on(CREATE_BLOCK)
    def can_create_block(agent: ExternalAgent):
        """
            Behavior called on CREATE_BLOCK event. This is a system event triggered
            by the Environment.

            It is a one time authorization to create and propose a new Block to the network.
        """

        agent.propose_block(agent.create_block([]))

    @staticmethod
    @export
    def create_block(agent: ExternalAgent, transactions: list[Transaction]) -> Block:
        """ Creates a block with the given transactions

            :param transactions: the transactions to include in the block
            :type transactions: list[Transaction]
            :returns: the block with the transactions included in it
            :rtype: Block
        """
        head_hash = agent.context['blockchain'].head.hash
        return Block(head_hash, agent.name, transactions)

    @staticmethod
    @export
    def propose_block(agent: ExternalAgent, block: Block):
        """ Propose a block to the network

            :param block: the block to propose to the network
            :type block: Block
        """
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseBlock(agent.name, block), outbound_peers)
