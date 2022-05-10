
"""
    Block file class implementation
"""

import hashlib
from .transaction import Transaction
from ..agent import Agent


class Block():

    """
        Block class implementation :

        A Block is an ordered set of Transactions, and is aimed to be
        included in a Blockchain.
    """

    def __init__(self, parent_hash: str, creator: str, transactions: list[Transaction]) -> None:
        self._parent_hash = parent_hash
        self._transactions = transactions
        self._creator = creator
        self._hash = self.compute_hash()
        self._total_fees = sum(map(lambda tx: tx.fee, self._transactions))
        self._height = 0

    @property
    def parent_hash(self) -> "str":
        """ Get the hash of the parent Block

            :returns: the hash of the parent Block
            :rtype: str
        """
        return self._parent_hash

    @property
    def transactions(self) -> list[Transaction]:
        """ Get the Transactions contained within the Block

            :returns: the Transaction included in the Block
            :rtype: list[Transaction]
        """
        return self._transactions

    @property
    def creator(self) -> Agent:
        """ Get the Agent that created the Block

            :returns: the Agent that created the Block
            :rtype: Agent
        """
        return self._creator

    @property
    def total_fees(self) -> int:
        """ Get the sum of the fees of all Transactions contained in the Block

            :returns: The total fees of the Block
            :rtype: int
        """
        return self._total_fees

    @property
    def hash(self) -> str:
        """ Get the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """
        return self._hash

    @property
    def height(self) -> int:
        """ Get the height of the Block

            This property is used internally by the Blockchain.
            It's default value is 0, and will be overwritten when
            the Block is successfully added to a Blockchain.

            :returns: the height of the Block in the Blockchain
            :rtype: int
        """
        return self._height

    @height.setter
    def height(self, new_height: int) -> None:

        if new_height < 0:
            raise ValueError("Block height cannot be negative")

        self._height = new_height

    def __str__(self) -> str:
        return self.serialize()

    def serialize(self) -> str:
        """ Serialize the Block

            :returns: the serialized Block
            :rtype: str
        """
        serialized_txs = ','.join((map(str, self._transactions)))
        return f'{{ parentHash: {self._parent_hash} - creator: {self._creator} - transactions: {serialized_txs} }}'

    def compute_hash(self) -> str:
        """ Computes the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """
        return hashlib.sha256(self.serialize().encode()).hexdigest()
