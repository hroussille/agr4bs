from ..Agent import Agent, StateChange
from ..Role import Role, RoleType
from ..Common import Transaction


class TransactionEndorserStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        def _transactionEndorsementStrategy():
            return True

        self.transactionEndorsementStrategy = _transactionEndorsementStrategy


class TransactionEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_ENDORSER)

    @staticmethod
    def stateChange() -> StateChange:
        return TransactionEndorserStateChange()

    @staticmethod
    def endorseTransaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Endorse a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to endorse
            :type transaction: Transaction
            :returns: wether the transaction was endorsed or not
            :rtype: bool
        """
        raise NotImplementedError
