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

from ....roles import Role, RoleType
from ....agents import Agent, ContextChange, AgentType
from ..blockchain import Payload, Transaction
from ....common import on, export
from ....network.messages import DiffuseTransaction
from ....events import CREATE_TRANSACTION


class TransactionProposerContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (TransactionProposer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        self.nonce = 0


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
    @export
    def create_transaction(agent: Agent, fee: int, amount: int, payload: Payload, receiver: str) -> Transaction:
        """ Create a transaction with the given payload for the given receiver

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param payload: the payload of the transaction
            :type payload: Payload
            :param receiver: the receiver of the transaction
            :type receiver: Agent
        """

        if not agent.has_role(RoleType.BLOCKCHAIN_MAINTAINER):
            return

        nonce = agent.context['state'].get_account_nonce(agent.name)

        return agent.context['factory'].build_transaction(agent.name, receiver, nonce, fee=fee, amount=amount, payload=payload)

    @staticmethod
    @export
    def propose_transaction(agent: Agent, transaction: Transaction) -> None:
        """ Propose a transaction to the network

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to propose to the network
            :type transaction: Transaction
        """
        outbound_peers = list(agent.context['outbound_peers'])
        agent.receive_transaction(transaction)
        agent.send_message(DiffuseTransaction(
            agent.name, transaction), outbound_peers)

    @staticmethod
    @export
    @on(CREATE_TRANSACTION)
    def create_and_propose_transaction(agent: Agent, fee: int, amount: int, payload: Payload, receiver: str) -> None:

        transaction = agent.create_transaction(fee, amount, payload, receiver)

        if transaction is not None:
            agent.propose_transaction(transaction)
