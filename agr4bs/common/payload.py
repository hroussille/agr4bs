"""
    Payload file class implementation
"""


from .serializable import Serializable


class Payload(Serializable):

    """
        Payload class implementation :

        A Payload is essentially some data that is included into a Transaction.
    """

    def __init__(self, data: bytes = None):

        if data is None:
            data = bytes()

        if not isinstance(data, bytes):
            raise TypeError(
                f'Invalid Payload data type. Got {type(data)} expected <class \'bytes\'>')

        self._data = data

    @property
    def data(self) -> str:
        """ Get the data of the Payload

            :returns: the data of the Payload
            :rtype: str
        """
        return self._data

    def serialize(self) -> bytes:
        """ Serialize the Payload

            :returns: the serialized Payload
            :rtype: str
        """
        return self._data

    def __str__(self) -> str:
        return self.serialize()
