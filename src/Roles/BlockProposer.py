from Role import Role, RoleType
from Common.Transaction import Transaction
from src.Common.Block import Block


class BlockProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_PROPOSER)

    def selectTransaction(self, transactions: list[Transaction], *args, **kwargs) -> list[Transaction]:
        """ Select a subset of transactions for inclusion in a block

            :param transactions: the available transactions
            :type transactions: list[Transaction]
            :returns: the list of selected transactions
            :rtype: list[Transaction]
        """
        raise NotImplementedError

    def createBlock(self, transactions: list[Transaction], *args, **kwargs) -> Block:
        """ Creates a block with the given transactions

            :param transactions: the transactions to include in the block
            :type transactions: list[Transaction]
            :returns: the block with the transactions included in it
            :rtype: Block
        """
        raise NotImplementedError

    def proposeBlock(self, block: Block, *args, **kwargs):
        """ Propose a block to the network

            :param block: the block to propose to the network
            :type block: Block
        """
        raise NotImplementedError
