"""
    Account file class implementation
"""

import pickle


class Account:

    """
        An account keeps track of several informations bound to a single identity
        (i.e., agent_name or address), such as :

        - balance
        - nonce
        - internal_agent (smart contract)
        - storage
    """

    # pylint: disable=too-many-arguments
    def __init__(self, account_name: str, balance: int = 0, nonce: int = 0, internal_agent=None, storage=None):
        self._name = account_name
        self._balance = balance

        if storage is None:
            storage = {}

        self._internal_agent = internal_agent
        self._storage = storage
        self._nonce = nonce

    @property
    def balance(self) -> int:
        """
            Get the balance of the Account
        """
        return self._balance

    def add_balance(self, to_add: int):
        """
            Add to_add to the balance of the Account
        """
        self._balance = self._balance + to_add

    def remove_balance(self, to_remove: int):
        """
            Remove to_remove from the balance of the Account
        """
        self._balance = self._balance - to_remove

    def increment_nonce(self):
        """
            Increment the nonce of the Account
        """
        self._nonce = self._nonce + 1

    def decrement_nonce(self):
        """
            Decrement the nonce of the Account
        """
        self._nonce = self._nonce - 1

    @property
    def nonce(self):
        """
            Get the nonce of the Account
        """
        return self._nonce

    @property
    def name(self):
        """
            Get the name (address) of the Account
        """
        return self._name

    @property
    def internal_agent(self):
        """
            Get the handler of the Account
        """
        return self._internal_agent

    @property
    def storage(self):
        """
            Get the storage of the Account
        """
        return self._storage

    def set_storage_at(self, key: str, value: any):
        """
            Set storage[key] to the given value
        """
        if value is None and key in self._storage.keys():
            del self._storage[key]

        self._storage[key] = value

    def get_storage_at(self, key: str):
        """
            Get storage[key]
        """
        if key in self._storage:
            return self._storage[key]

        return None

    def update_storage(self, new_storage: dict):
        """
            Update the storage of the current Account with a new value
        """
        self._storage = new_storage

    def copy(self):
        """
            Copy the current Account
        """
        save_internal_agent = self.internal_agent
        self._internal_agent = None

        copy = pickle.loads(pickle.dumps(self))
        copy._internal_agent = save_internal_agent

        self._internal_agent = save_internal_agent

        return copy
