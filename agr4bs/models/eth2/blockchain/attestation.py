
"""
    Attestation file class implementation
"""

from ....common import Serializable


class Attestation(Serializable):

    """
        Attestation class implementation :

        An Attestation is essentially a vote on the current state of the blockchain.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, agent_name: str, epoch:int, slot: int, index: int, root: str, source: str,  target: str) -> None:

        self._agent_name = agent_name
        self._epoch = epoch
        self._slot = slot
        self._index = index
        self._root = root
        self._source = source
        self._target = target

    @property
    def agent_name(self) -> str:
        """
            Get the name of the agent that created the attestation

            :returns: The name of the agent that created the
        """
        return self._agent_name
    
    @property
    def epoch(self) -> int:
        """
            Get the epoch of the Attestation

            :returns: The epoch of the attestation
        """
        return self._epoch
    
    @property
    def slot(self) -> int:
        """ Get the slot of the Attestation

            :returns: The slot of the attestation
            :rtype: int
        """
        return self._slot

    @property
    def index(self) -> int:
        """ Get the committee index of the Attestation

            :returns: The committee index of the attestation
            :rtype: int
        """
        return self._index

    @property
    def root(self) -> str:
        """ Get the root_hash of the Attestation
            This is the block that the validator sees as the head of the chain.

            :returns: The root_hash of the attestation
            :rtype: str
        """
        return self._root

    @property
    def source(self) -> str:
        """ Get the source block hash of the Attestation
            The most recent justified block from the perspective of the validator.

            :returns: The source block hash of the attestation
            :rtype: str
        """
        return self._source

    @property
    def target(self) -> str:
        """ Get the target block hash of the Attestation
            The first block in the current epoch from the perspective of the validator.

            :returns: The target block hash of the attestation
            :rtype: str
        """
        return self._target

    def __str__(self) -> str:
        return f"Epoch: {self._epoch} Slot: {self._slot}, Index: {self._index}, Root: {self._root}, Source: {self._source}, Target: {self._target}"

    def checkpoint_vote_str(self) -> str:
        """
            Return the checkpoint vote informations as a string
        """
        return f"Epoch: {self._epoch} Slot: {self._slot}, Source: {self._source}, Target: {self._target}"

    def __hash__(self) -> int:
        return hash(self._agent_name) + hash(self._epoch) + hash(self._slot) + hash(self._index) + hash(self._root) + hash(self._source) + hash(self._target)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Attestation):
            return False
        
        return self._agent_name == other.agent_name and self._epoch == other.epoch and self._slot == other.slot and self._index == other.index and self._root == other.root and self._source == other.source and self._target == other.target