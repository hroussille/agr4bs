
"""
    Block file class implementation
"""

import hashlib
import pickle
from ....blockchain import IBlockHeader, IBlock
from .attestation import Attestation
from .transaction import Transaction
from ..constants import SLOTS_PER_EPOCH


class BlockHeader(IBlockHeader):

    """
        Block Header class implementation
    """

    def __init__(self,  parent_hash: str, creator: str, hash: str) -> None:
        super().__init__(parent_hash, creator, hash)


class Block(IBlock):

    """
        Block class implementation :

        A Block is an ordered set of Transactions, and is aimed to be
        included in a Blockchain.

        In Ethereum 2.0 additional informations are included to account for
        the status of the block
    """

    def __init__(self, parent_hash: str, creator: str, slot: int, transactions: list[Transaction] = None) -> None:

        self._justified = False
        self._finalized = False
        self._slot = slot
        self._attestations = []
        self._seed = 0

        super().__init__(parent_hash, creator, transactions)

    @property
    def justified(self) -> bool:
        """
            Get the justified status of the Block
        """
        return self._justified

    @justified.setter
    def justified(self, value: bool) -> None:
        """
            Set the justified status of the Block
        """
        self._justified = value

    @property
    def finalized(self) -> bool:
        """
            Get the finalized status of the Block
        """
        return self._finalized

    @property
    def slot(self) -> int:
        """
            Get the slot of the Block
        """
        return self._slot
    
    @property
    def epoch(self) -> int:
        """
            Get the epoch of the Block
        """
        return self._slot // SLOTS_PER_EPOCH
    
    @property
    def seed(self) -> int:
        """
            Get the seed of the Block
        """
        return self._seed
    
    @seed.setter
    def seed(self, value: int) -> None:
        """
            Set the seed of the Block
        """
        self._seed = value

    @finalized.setter
    def finalized(self, value: bool) -> None:
        """ 
            Set the finalized status of the Block
        """
        self._finalized = value

    @property
    def attestations(self) -> dict:
        """
            Get the attestations of the Block
        """
        return self._attestations

    def add_attestation(self, attestation: Attestation) -> None:
        """
            Add an attestation to the Block
        """
        if attestation not in self._attestations:
            self._attestations.append(attestation)
            return

        raise ValueError(
            "Dupplicated attestation for agent " + attestation.agent_name)

    def compute_hash(self) -> str:
        """ Computes the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """

        hash_dict = {
            'number': self._number,
            'parent_hash': self._parent_hash,
            'creator': self._creator,
            'total_fees': self._total_fees,
            'transactions': list(map(lambda tx: tx.compute_hash(), self._transactions)),
            'slot': self._slot,
            'seed': self._seed
        }

        return hashlib.sha256(pickle.dumps(hash_dict)).hexdigest()
