from ..Agent import Agent, StateChange
from ..Role import Role, RoleType
from ..Common import Transaction
from ..Common import Block


class BlockProposerStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        self.transactionSelectionStrategy = None


class BlockProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_PROPOSER)

    @staticmethod
    def stateChange() -> StateChange:
        return BlockProposerStateChange()

    @staticmethod
    def selectTransaction(agent: Agent, transactions: list[Transaction], *args, **kwargs) -> list[Transaction]:
        """ Select a subset of transactions for inclusion in a block

            :param transactions: the available transactions
            :type transactions: list[Transaction]
            :returns: the list of selected transactions
            :rtype: list[Transaction]
        """
        raise NotImplementedError

    @staticmethod
    def createBlock(agent: Agent, transactions: list[Transaction], *args, **kwargs) -> Block:
        """ Creates a block with the given transactions

            :param transactions: the transactions to include in the block
            :type transactions: list[Transaction]
            :returns: the block with the transactions included in it
            :rtype: Block
        """
        raise NotImplementedError

    @staticmethod
    def proposeBlock(block: Block, *args, **kwargs):
        """ Propose a block to the network

            :param block: the block to propose to the network
            :type block: Block
        """
        raise NotImplementedError
