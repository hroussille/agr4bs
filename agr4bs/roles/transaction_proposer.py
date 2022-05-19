"""
Abstract implementation of the TransactionProposer role as per AGR4BS

TransactionProposerContextChange:

The TransactionProposerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

TransactionProposer:

The TransactionProposer implementation which MUST contain the following :
- create_transaction
- propose_transaction

"""

from .role import Role, RoleType
from ..agents import Agent, ContextChange, AgentType
from ..common import Payload, Transaction


class TransactionProposerContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (TransactionProposer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        pass


class TransactionProposer(Role):

    """
        Implementation of the TransactionProposer Role which must
        expose the following behaviors :
        - create_transaction
        - propose_transaction

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_PROPOSER, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return TransactionProposerContextChange()

    @staticmethod
    def create_transaction(agent: Agent, paylaod: Payload, receiver: Agent) -> Transaction:
        """ Create a transaction with the given payload for the given receiver

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param payload: the payload of the transaction
            :type payload: Payload
            :param receiver: the receiver of the transaction
            :type receiver: Agent
        """
        raise NotImplementedError

    @staticmethod
    def propose_transaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> None:
        """ Propose a transaction to the network

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to propose to the network
            :type transaction: Transaction
        """
        raise NotImplementedError
