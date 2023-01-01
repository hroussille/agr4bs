
"""
    Block file class implementation
"""

import hashlib
import pickle
from ..common import Serializable
from .transaction import ITransaction

class IBlockHeader(Serializable):

    """
        Block Header class implementation
    """

    def __init__(self,  parent_hash: str, creator: str, hash: str) -> None:
        self._creator = creator
        self._parent_hash = parent_hash
        self._hash = hash

class IBlock(Serializable):

    """
        Block class implementation :

        A Block is an ordered set of Transactions, and is aimed to be
        included in a Blockchain.
    """

    _nonce = 0

    def __init__(self, parent_hash: str, creator: str, transactions: list[ITransaction] = None) -> None:
        self._parent_hash = parent_hash

        if transactions is None:
            transactions = []

        self._transactions = transactions
        self._creator = creator
        self._total_fees = sum(map(lambda tx: tx.fee, self._transactions))
        self._height = 0

        self._number = IBlock._nonce
        IBlock._nonce = IBlock._nonce + 1

        self._hash = self.compute_hash()
        self._invalid = False


    @property
    def header(self) -> IBlockHeader:
        """
            Get the header of the block
        """
        return IBlockHeader(self._parent_hash, self._creator, self._hash)
        
    @property
    def parent_hash(self) -> "str":
        """ Get the hash of the parent Block

            :returns: the hash of the parent Block
            :rtype: str
        """
        return self._parent_hash

    @property
    def total_fees(self) -> int:
        """ Get the sum of the fees of all Transactions contained in the Block

            :returns: The total fees of the Block
            :rtype: int
        """
        return self._total_fees

    @property
    def transactions(self) -> list[ITransaction]:
        """ Get the Transactions contained within the Block

            :returns: the Transaction included in the Block
            :rtype: list[ITransaction]
        """
        return self._transactions

    @property
    def creator(self) -> str:
        """ Get the Agent that created the Block

            :returns: the Agent that created the Block
            :rtype: Agent
        """
        return self._creator

    @property
    def hash(self) -> str:
        """ Get the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """
        return self._hash

    @hash.setter
    def hash(self, value: str):
        """
            Manually set the hash of the Block
        """
        self._hash = value

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

    @property
    def invalid(self) -> bool:

        """
            Get the invalid status of a block
        """

        return self._invalid
    
    @invalid.setter
    def invalid(self, invalid: bool) -> None:
        self._invalid = invalid

    def compute_hash(self) -> str:
        """ Computes the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """

        hash_dict = {'number': self._number, 'parent_hash': self._parent_hash, 'creator': self._creator,
                     'total_fees': self._total_fees, 'transactions': list(map(lambda tx: tx.compute_hash(), self._transactions))}

        return hashlib.sha256(pickle.dumps(hash_dict)).hexdigest()

    def __eq__(self, __o: object) -> bool:

        if not isinstance(__o, IBlock):
            return False

        return self._hash == __o.compute_hash()
