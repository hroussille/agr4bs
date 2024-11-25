
"""
    DefaultVM file class implementation
"""
from enum import Enum

from agr4bs.agents.internal_agent import InternalAgentDeployement, Success
from .execution_context import ExecutionContext
from ..state import State, Account, Receipt
from ..state import CreateAccount, AddBalance, RemoveBalance, IncrementAccountNonce
from ..blockchain import ITransaction
from ..agents import InternalAgent, InternalAgentCalldata, InternalAgentResponse, Revert

DEPTH_LIMIT = 32

class TransactionType(Enum):
    """
        Valid transaction types
    """
    TRANSFER = "TRANSFER"
    CALL = "CALL"
    DEPLOYEMENT = "DEPLOYEMENT"
    NOOP = "NOOP"


class IVM:

    """
        Default Virtual Machine class implementation

        The virtual machine process tx and executes them on a mirror State
        it should be able to process :

        - ExternalAgent to ExternalAgent transactions
        - ExternalAgent to InternalAgent transactions
        - InternalAgent to InternalAgent transactions
        - InternalAgent to ExternalAgent transactions
    """

    def __init__(self):
        pass

    @staticmethod
    def process_tx(state: State, tx: ITransaction) -> Receipt:
        raise NotImplementedError
