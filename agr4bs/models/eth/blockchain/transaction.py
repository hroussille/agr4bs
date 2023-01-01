"""
    Transaction file class implementation
"""

import hashlib
import pickle

from ....common import Serializable
from .payload import Payload


class Transaction(Serializable):

    """
        Transaction class implementation :

        A Transaction is essentially a transfer from one Agent to another.
        it may be used to send currency, or to trigger arbitrary logic if
        it targets a smart contract Agent.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, origin: str, to: str, nonce: int, fee: int = 0,  value: int = 0, payload: Payload = None) -> None:
        self._origin = origin
        self._to = to
        self._value = value
        self._fee = fee
        self._nonce = nonce

        if payload is None:
            payload = Payload()

        self._payload = payload
        self._hash = self.compute_hash()

    @property
    def origin(self) -> str:
        """ Get the name of the Agent at the origin of the Transaction

            :returns: the name of the Agent that sent the Transaction
            :rtype: str
        """
        return self._origin

    @property
    def to(self) -> str:
        """ Get the name of the Agent recipient of the Transaction

            :returns: the name of the Agent recipent of the Transaction
            :rtype: str
        """
        return self._to

    @property
    def nonce(self) -> int:
        """ Get the nonce of the Transaction

            :returns: the nonce of the Transaction
            :rtype: int
        """
        return self._nonce

    @property
    def value(self) -> int:
        """ Get the value sent within the Transaction

            :returns: the value sent within the Transaction
            :rtype: int
        """
        return self._value

    @property
    def fee(self) -> int:
        """ Get the fee sent alongside the Transaction

            :returns: the fee sent alongside the Transaction
            :rtype: int
        """
        return self._fee

    @property
    def payload(self) -> Payload:
        """ Get the Payload (i.e., data) sent within the Transaction

            :returns: the Payload within the Transaction
            :rtype: Payload
        """
        return self._payload

    @property
    def hash(self) -> str:
        """ Get the hash of the Transaction

            :returns: The hash of the Transaction
            :rtype: str
        """
        return self._hash

    @hash.setter
    def hash(self, _hash) -> None:
        """
            Set the hash of the Transaction
        """
        self._hash = _hash

    def compute_hash(self) -> str:
        """ Computes the hash of the Block

            :returns: The hash of the Block
            :rtype: str
        """
        hash_dict = {'from': self._origin, 'to': self._to,
                     'value': self._value, 'fee': self._fee, 'payload': self._payload.serialize(), 'nonce': self._nonce}

        return hashlib.sha256(pickle.dumps(hash_dict)).hexdigest()

    def __eq__(self, __o: object) -> bool:

        if not isinstance(__o, Transaction):
            return False

        return self._hash == __o.compute_hash()
