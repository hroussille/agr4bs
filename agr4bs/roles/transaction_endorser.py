"""
Abstract implementation of the TransactionEndorser role as per AGR4BS

TransactionEndorserStateChange:

The TransactionEndorserStateChange exposes changes that need to be made to the
Agent state when the Role is mounted and unmounted.

TransactionEndorser:

The TransactionProposer implementation which MUST contain the following :
- endorse_transaction
"""

from ..agent import Agent, StateChange
from ..role import Role, RoleType
from ..common import Transaction


class TransactionEndorserStateChange(StateChange):
    """
        State changes that need to be made to the Agent when
        the associated Role (TransactionEndorser) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        def _transaction_endorsement_strategy():
            return True

        self.transaction_endorsement_strategy = _transaction_endorsement_strategy


class TransactionEndorser(Role):
    """
        Implementation of the TransactionEndorser Role which must
        expose the following behaviors :
        - endorse_transaction

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_ENDORSER)

    @staticmethod
    def state_change() -> StateChange:
        return TransactionEndorserStateChange()

    @staticmethod
    def endorse_transaction(agent: Agent, transaction: Transaction, *args, **kwargs) -> bool:
        """ Endorse a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param transaction: the transaction to endorse
            :type transaction: Transaction
            :returns: wether the transaction was endorsed or not
            :rtype: bool
        """
        raise NotImplementedError
