
"""
    DefaultVM file class implementation
"""

from ..state import State, Account, Receipt, StateChange
from ..state import CreateAccount, AddBalance, RemoveBalance, IncrementAccountNonce
from ..common import Transaction, Payload


#pylint: disable=too-few-public-methods
class DefaultVM:

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

    def process_tx(self, state: State, tx: Transaction) -> Receipt:
        """
            Process a tx according to the given State and returns the tx Receipt
        """

        reverted = False
        pre_changes = [IncrementAccountNonce(tx.origin)]
        changes = []

        if tx.amount > 0:

            if state.get_account(tx.to) is None:
                pre_changes.append(CreateAccount(Account(tx.to)))

            pre_changes.append(RemoveBalance(tx.origin, tx.amount))
            pre_changes.append(AddBalance(tx.to, tx.amount))

        state.apply_batch_state_change(pre_changes + changes)

        recipient_account = state.get_account(tx.to)

        if recipient_account is not None and recipient_account.internal_agent is not None:
            reverted, internal_changes = self._internal_call(
                state, tx.origin, tx.to, tx.payload)
            changes = changes + internal_changes

        return Receipt(tx.hash, pre_changes + changes, reverted)

    def _internal_call(self, state: State, _from: str, to: str, payload: Payload) -> tuple[bool, list[StateChange]]:
        raise NotImplementedError()
