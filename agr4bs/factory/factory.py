"""
    Agr4bsFactory file class implementation
"""

from ..network import Network
from ..blockchain import IBlockchain, IBlock, ITransaction, Payload
from ..state import State
from ..vm import IVM


class IFactory:

    """
        The Agr4bsFactory is the core factory for all common structures
        - Blockchain
        - Block
        - Transaction
        - Payload
    """

    __network = None
    __tx_pool = None

    @staticmethod
    def build_blockchain(genesis: IBlock) -> IBlockchain:
        """
            Builds a black box blockchain implementation.
        """
        raise NotImplementedError

    @staticmethod
    def build_block(parent_hash: str, creator: str, transactions: list[ITransaction] = None) -> IBlock:
        """
            Builds a black box Block implementation
        """
        return IBlock(parent_hash, creator, transactions)

    @staticmethod
    def build_transaction(origin: str, to: str, nonce: int, fee: int = 0, amount: int = 0, payload: Payload = None) -> ITransaction:
        """
            Builds a black box Transaction implementation
        """
        return ITransaction(origin, to, nonce, fee, amount, payload)

    @staticmethod
    def build_payload(data=None) -> Payload:
        """
            Builds a black box Payload implementation
        """
        return Payload(data)

    @staticmethod
    def build_vm() -> IVM:
        """
            Builds a black box VM implementation
        """
        raise NotImplementedError

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
        if IFactory.__network is None or reset is True:
            IFactory.__network = Network(delay=200, drop_rate=0.005)

        return IFactory.__network

    @staticmethod
    def build_tx_pool() -> dict[dict[ITransaction]]:
        """
            Builds a black box tx pool implementation

            - This can be a singleton : shared tx pool accross all agents, or a new instance
            everytime meaning that all agents maintain an individual tx pool
        """
        return {}

    @staticmethod
    def build_shared_tx_pool(reset=False) -> dict[dict[ITransaction]]:
        """
            Builds a black box shared tx pool implementation
        """
        if IFactory.__tx_pool is None or reset is True:
            IFactory.__tx_pool = {}

        return IFactory.__tx_pool
