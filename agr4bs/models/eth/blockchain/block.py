
"""
    Block file class implementation
"""

import hashlib
import pickle
from ....common import Serializable
from .transaction import Transaction
from ....blockchain import IBlockHeader, IBlock


class BlockHeader(IBlockHeader):

    """
        Block Header class implementation
    """

    def __init__(self,  parent_hash: str, creator: str, hash: str) -> None:
        super().__init__(parent_has, creator, hash)


class Block(IBlock):

    """
        Block class implementation :

        A Block is an ordered set of Transactions, and is aimed to be
        included in a Blockchain.
    """

    def __init__(self, parent_hash: str, creator: str, transactions: list[Transaction] = None) -> None:
        super().__init__(parent_hash, creator, transactions)


