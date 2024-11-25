from ..blockchain import Blockchain, Block, Attestation
from .beacon_state import BeaconState

class ForkChoice:

    """
        Fork choice rule for the beacon chain
        This class implements the LMD GHOST algorithm
    """

    def __init__(self, blockchain: Blockchain) -> None:
        
        self._blockchain: Blockchain = blockchain
        self._validators = []
        self._votes = {}
        self._weights = {}

        # effective balances are stored in wei
        self._effective_balances = {}
        self._total_active_balance = 0
        
        assert blockchain.genesis.justified and blockchain.genesis.finalized

    def set_effective_balances(self, effective_balances: dict) -> None:
        """
            Set the effective balances
        """
        self._effective_balances = effective_balances
        self._total_active_balance = sum(effective_balances.values())

    def prune(self) -> None:
        """
            Prune the underlying tree by removing all the blocks
            that are below the finalized checkpoint
        """

    def process_attestation(self, attestation: Attestation) -> None:
        """
            Add a new block vote to the tree and update the weights
        """

        # This attestation is not from a known validator
        if attestation.agent_name not in self._validators:
            return
        
        # This attestation is already in the tree
        if self._votes[attestation.agent_name] is not None and self._votes[attestation.agent_name] == attestation:
            return

        root = self._blockchain.get_block(attestation.root)

        # This attestation is voting for an uknown head block
        if root is None:
            return
        

    