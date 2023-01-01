"""
    Payload file class implementation
"""


from ....common import Serializable


class Payload(Serializable):

    """
        Payload class implementation :

        A Payload is essentially some data that is included into a Transaction.
        This data may be executed / interpreted, informative or simply vanity data.
    """

    def __init__(self, data: bytes = None):

        if data is None:
            data = bytes()

        if not isinstance(data, bytes):
            raise TypeError(
                f'Invalid Payload data type. Got {type(data)} expected <class \'bytes\'>')

        self._data = data

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Payload):
            return False

        return __o.data == self._data

    @property
    def data(self) -> str:
        """ Get the data of the Payload

            :returns: the data of the Payload
            :rtype: str
        """
        return self._data
