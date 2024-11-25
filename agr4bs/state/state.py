"""
    State file class implementation
"""

from math import inf
import pickle
import copy
from .state_change import StateChange, StateChangeType
from .state_change import UpdateAccountStorage
from .state_change import CreateAccount, DeleteAccount
from .state_change import AddBalance, RemoveBalance
from .state_change import IncrementAccountNonce, DecrementAccountNonce
from .account import Account


class State:

    """
        State class implementation :

        A State is a ensemble of informations about the Blockchain at a specific
        point in time.

        The State is meant to be updated on every new Block included in the Blockchain.
        It contains informations such as the balances, nonces and so on of every known
        participant whose actions were recorded on the Blockchain.
    """

    def __init__(self) -> None:
        self._receipts: dict(Receipt) = {}
        self._accounts: dict(Account) = {}
        self._create_account(CreateAccount(Account('genesis', inf)))

    def _apply_jump_table(self, state_change_type: StateChangeType) -> None:
        """
            Helper function to get the appropriate handler from a StateChangeType
        """
        return {
            StateChangeType.CREATE_ACCOUNT: self._create_account,
            StateChangeType.DELETE_ACCOUNT: self._delete_account,
            StateChangeType.ADD_BALANCE: self._add_balance,
            StateChangeType.REMOVE_BALANCE: self._remove_balance,
            StateChangeType.INCREMENT_ACCOUNT_NONCE: self._increment_account_nonce,
            StateChangeType.DECREMENT_ACCOUNT_NONCE: self._decrement_account_nonce,
            StateChangeType.UPDATE_ACCOUNT_STORAGE: self._update_account_storage,
        }[state_change_type]

    def apply_batch_state_change(self, state_changes: list[StateChange]) -> None:
        """
            Apply all the changes described in state_changes

            :param state_changes: the list of changes that need to be applied to the state
            :type state_changes: list[StateChange]
        """
        for state_change in state_changes:
            self.apply_state_change(state_change)

    def apply_state_change(self, state_change: StateChange) -> None:
        """
            Apply the change described in state_change

            :param state_change: the changes that need to be applied to the state
            :type state_change: StateChange
        """
        handler = self._apply_jump_table(state_change.type)
        handler(state_change)

    def _add_balance(self, state_change: AddBalance):
        """
            Internal method: Add to the balance of an Account
        """
        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot add balance to non existing Account")

        self._accounts[state_change.account_name].add_balance(
            state_change.value)

    def _remove_balance(self, state_change: RemoveBalance):
        """
            Internal method: remove balance from an Account
        """
        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot remove balance from non existing Account")

        self._accounts[state_change.account_name].remove_balance(
            state_change.value)

    def _create_account(self, state_change: CreateAccount):
        """
            Internal method: create a new Account
        """

        if self.has_account(state_change.account_name):
            raise ValueError("Cannot create already existing Account")

        self._accounts[state_change.account_name] = state_change.account

    def _delete_account(self, state_change: DeleteAccount):
        """
            Internal method: delete an Account
        """
        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot delete non existing Account")

        del self._accounts[state_change.account_name]

    def _increment_account_nonce(self, state_change: IncrementAccountNonce):
        """
            Internal method: increment an Account nonce
        """

        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot increment nonce of non existing Account")

        self._accounts[state_change.account_name].increment_nonce()

    def _decrement_account_nonce(self, state_change: DecrementAccountNonce):
        """
            Internal method: decrement an Account nonce
        """

        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot decrement nonce of non existing Account")

        self._accounts[state_change.account_name].decrement_nonce()

    def _update_account_storage(self, state_change: UpdateAccountStorage):
        """
            Update the storage of a specific Account
        """

        if not self.has_account(state_change.account_name):
            raise ValueError("Cannot update storage of non existing Account")

        new_storage = self.get_account_storage(
            state_change.account_name) + state_change.delta_apply

        self._accounts[state_change.account_name].update_storage(new_storage)

    def account_names(self) -> list[str]:
        """
            Get the list of known accounts names
        """
        return list(self._accounts.keys())

    def has_account(self, account_name: str) -> bool:
        """
            Get a boolean indicator to know if the Account is
            present in the state or not
        """
        return account_name in self._accounts

    def get_account(self, account_name: str) -> Account:
        """
            Get a specific Account from the State
        """
        if not self.has_account(account_name):
            return None

        return self._accounts[account_name].copy()

    def get_account_nonce(self, account_name: str) -> int:
        """
            Get a specific Account nonce from the State
        """
        if not self.has_account(account_name):
            return 0

        return self._accounts[account_name].nonce

    def get_account_balance(self, account_name: str) -> int:
        """
            Get a specific Account balance from the state
        """
        if not self.has_account(account_name):
            return 0

        return self._accounts[account_name].balance

    def get_account_storage(self, account_name: str) -> dict:
        """
            Get a specific Account storage from the state.
        """
        account = self.get_account(account_name)

        if account is None:
            return None

        return account.storage

    def get_account_storage_at(self, account_name: str, key: any) -> any:
        """
            Get the value at "key" from a specified account storage
        """
        account = self.get_account(account_name)

        if account is None:
            return None

        return account.get_storage_at(key)

    def get_account_internal_agent(self, account_name: str) -> 'InternalAgent':
        """
            Get a specific Account InternalAgent from the state
        """
        account = self.get_account(account_name)

        if account is None:
            return None

        return account.internal_agent

    def copy(self) -> 'State':
        """
            Copy the current State
        """
        #return copy.deepcopy(self)
        return pickle.loads(pickle.dumps(self))