
"""
    Block file class implementation
"""

from ....blockchain import IBlockHeader, IBlock
from .attestation import Attestation
from .transaction import Transaction

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

        super().__init__(parent_hash, creator, transactions)

        self._justified = False
        self._finalized = False
        self._slot = slot
        self._attestations = []

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

        raise ValueError("Dupplicated attestation for agent " + attestation.agent_name)       

