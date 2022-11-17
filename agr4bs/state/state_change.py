"""
    StateChange file class implementation
"""

from enum import Enum
from deepdiff import Delta
from .account import Account


class StateChangeType(Enum):

    """
        Enumeration of the allowed state operations
    """

    # Account data structure related operations
    CREATE_ACCOUNT = "create_account_name"
    DELETE_ACCOUNT = "delete_account_name"

    # Account balance related operations
    ADD_BALANCE = "add_balance"
    REMOVE_BALANCE = "remove_balance"

    # Account Nonce related operations
    INCREMENT_ACCOUNT_NONCE = "increment_account_name_nonce"
    DECREMENT_ACCOUNT_NONCE = "decrement_account_name_nonce"

    # Account Storage related operations
    UPDATE_ACCOUNT_STORAGE = "set_account_name_storage"


class StateChange():

    """
        State changes that need to be made to the State when the underlying
        Blockchain is updated.
    """

    def __init__(self, _type: StateChangeType, account_name: str) -> None:
        self._type = _type
        self._account_name = account_name

    def revert(self) -> 'StateChange':
        """
            Returns the reverse StateChange of the current StateChange.
        """
        raise NotImplementedError("Called revert on base StateChange class.")

    @property
    def type(self):
        """
            Get the type of the underlying StateChange operation
        """
        return self._type

    @property
    def account_name(self):
        """
            Get the Account name pointed by this state change operation
        """
        return self._account_name

    def __str__(self):
        return f"type: {self._type} account: {self._account_name}"


class AddBalance(StateChange):

    """
        StateChange to modify an Account's balance
    """

    def __init__(self, account_name: str, value: int):
        super().__init__(StateChangeType.ADD_BALANCE, account_name)
        self._value = value

    def revert(self) -> StateChange:
        return RemoveBalance(self._account_name, self._value)

    @property
    def value(self):
        """
            Get the vale change of the account_name balance
        """
        return self._value

    def __str__(self):
        return super().__str__() + f" value: {self._value}"

class RemoveBalance(StateChange):

    """
        StateChange to modify an Account's balance
    """

    def __init__(self, account_name: str, value: int):
        super().__init__(StateChangeType.REMOVE_BALANCE, account_name)
        self._value = value

    def revert(self) -> StateChange:
        return AddBalance(self._account_name, self._value)

    @property
    def value(self):
        """
            Get the vale change of the account_name balance
        """
        return self._value

    def __str__(self):
        return super().__str__() + f" value: {self._value}"


class CreateAccount(StateChange):

    """
        StateChange to create an account_name
    """

    def __init__(self, account: Account):

        super().__init__(StateChangeType.CREATE_ACCOUNT, account.name)
        self._account = account.copy()

    def revert(self) -> StateChange:
        return DeleteAccount(self._account)

    @property
    def account(self):
        """
            Get the Account data contained in the CreateAccount StateChange
        """
        return self._account.copy()


class DeleteAccount(StateChange):

    """
        StateChange to create an account_name
    """

    def __init__(self, account: Account):

        super().__init__(StateChangeType.DELETE_ACCOUNT, account.name)
        self._account = account.copy()

    def revert(self) -> StateChange:
        return CreateAccount(self._account)

    @property
    def account(self):
        """
            Get the Account data contained in the DeleteAccount StateChange
        """
        return self._account.copy()


class IncrementAccountNonce(StateChange):

    """
        StateChange to modify an Account nonce
    """

    def __init__(self, account_name: str):
        super().__init__(StateChangeType.INCREMENT_ACCOUNT_NONCE, account_name)

    def revert(self) -> StateChange:
        return DecrementAccountNonce(self._account_name)


class DecrementAccountNonce(StateChange):

    """
        StateChange to modify an Account nonce
    """

    def __init__(self, account_name: str):
        super().__init__(StateChangeType.DECREMENT_ACCOUNT_NONCE, account_name)

    def revert(self) -> StateChange:
        return IncrementAccountNonce(self._account_name)


class UpdateAccountStorage(StateChange):

    """
        StateChange to modify an Account Storage value
    """

    def __init__(self, account_name: str, delta_apply: Delta, delta_revert: Delta):
        super().__init__(StateChangeType.UPDATE_ACCOUNT_STORAGE, account_name)
        self._delta_apply = delta_apply
        self._delta_revert = delta_revert

    def revert(self) -> StateChange:
        return UpdateAccountStorage(self._account_name, self._delta_revert, self._delta_apply)

    @property
    def delta_apply(self):
        """
            Get the storage delta to apply the update
        """
        return self._delta_apply

    @property
    def delta_revert(self):
        """
            Get the storage delta to revert the update
        """
        return self._delta_revert
