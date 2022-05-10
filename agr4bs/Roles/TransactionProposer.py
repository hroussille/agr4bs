from ..Role import Role, RoleType
from ..Agent import Agent, StateChange
from ..Common import Transaction, Payload


class TransactionProposerStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()


class TransactionProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_PROPOSER)

    @staticmethod
    def state_change() -> StateChange:
        return TransactionProposerStateChange()

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
