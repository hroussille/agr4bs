"""
    Payload file class implementation
"""


class Payload():

    """
        Payload class implementation :

        A Payload is essentially some data that is included into a Transaction.
    """

    def __init__(self, data: str = None):

        if data is None:
            data = ""

        if not isinstance(data, str):
            raise TypeError(
                f'Invalid Payload data type. Got {type(data)} expected str')

        self._data = data

    @property
    def data(self) -> str:
        """ Get the data of the Payload

            :returns: the data of the Payload
            :rtype: str
        """
        return self._data

    def serialize(self) -> str:
        """ Serialize the Payload

            :returns: the serialized Payload
            :rtype: str
        """
        return self._data

    def __str__(self) -> str:
        return self.serialize()
