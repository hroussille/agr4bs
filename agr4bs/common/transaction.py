"""
    Transaction file class implementation
"""

from .payload import Payload


class Transaction():

    """
        Transaction class implementation :

        A Transaction is essentially a transfer from one Agent to another.
        it may be used to send currency, or to trigger arbitrary logic if
        it targets a smart contract Agent.
    """

    #pylint: disable=too-many-arguments
    def __init__(self, origin: str, to: str, amount: int = 0, fee: int = 0, payload: Payload = None) -> None:
        self._origin = origin
        self._to = to
        self._amount = amount
        self._fee = fee

        if payload is None:
            payload = Payload()

        self._payload = payload

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
    def amount(self) -> int:
        """ Get the amount sent within the Transaction

            :returns: the amount sent within the Transaction
            :rtype: int
        """
        return self._amount

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

    def __str__(self) -> str:
        return self.serialize()

    def serialize(self) -> str:
        """ Serialize the Transaction

            :returns: the serialized Transaction
            :rtype: str
        """
        return f'{{ from: {self._origin} - to: {self._to} - fee: {str(self.fee).zfill(10)} - amount: {str(self.amount).zfill(10)} - payload: {self._payload.serialize()} }}'
