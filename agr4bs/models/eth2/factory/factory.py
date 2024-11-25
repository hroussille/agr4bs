"""
    Ethereum 2.0 Factory file class implementation
"""

from ....blockchain import Payload
from ....network import Network
from ..blockchain import Blockchain, Block, Transaction
from ....state import State
from ...eth import VM


class Eth2Factory:

    """
        The Ethereum 2.0 is the core factory for all common Eth 2.0 structures
        - Blockchain
        - Block
        - Transaction
        - Payload
    """

    __network = None
    __tx_pool = None

    @staticmethod
    def build_blockchain(genesis: Block) -> Blockchain:
        """
            Builds a black box blockchain implementation.
        """
        return Blockchain(genesis)

    @staticmethod
    def build_block(parent_hash: str, creator: str, slot: int, transactions: list[Transaction] = None) -> Block:
        """
            Builds a black box Block implementation
        """
        if transactions is None:
            transactions = []

        return Block(parent_hash, creator, slot, transactions)

    @staticmethod
    def build_transaction(origin: str, to: str, nonce: int, fee: int = 0, amount: int = 0, payload: Payload = None) -> Transaction:
        """
            Builds a black box Transaction implementation
        """
        return Transaction(origin, to, nonce, fee, amount, payload)

    @staticmethod
    def build_payload(data=None) -> Payload:
        """
            Builds a black box Payload implementation
        """
        return Payload(data)

    @staticmethod
    def build_vm() -> VM:
        """
            Builds a black box VM implementation
        """
        return VM()

    @staticmethod
    def build_state() -> State:
        """
            Builds a black box State implementation
        """
        return State()

    @staticmethod
    def build_network(reset=False) -> Network:
        """
            Builds a black box Network implementation
        """
        if Eth2Factory.__network is None or reset is True:
            Eth2Factory.__network = Network(delay=200, drop_rate=0.02)

        return Eth2Factory.__network

    @staticmethod
    def build_tx_pool() -> dict[dict[Transaction]]:
        """
            Builds a black box tx pool implementation

            - This can be a singleton : shared tx pool accross all agents, or a new instance
            everytime meaning that all agents maintain an individual tx pool
        """
        return {}

    @staticmethod
    def build_shared_tx_pool(reset=False) -> dict[dict[Transaction]]:
        """
            Builds a black box shared tx pool implementation
        """
        if Eth2Factory.__tx_pool is None or reset is True:
            Eth2Factory.__tx_pool = {}

        return Eth2Factory.__tx_pool
