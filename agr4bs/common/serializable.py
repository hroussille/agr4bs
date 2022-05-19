
"""
    Serializable file class implementation
"""

import pickle

#pylint: disable=too-few-public-methods


class Serializable:

    """
        A Serializable can be serialized to a pickle byte array.
    """

    def serialize(self) -> bytes:
        """
            Serialize the current object
        """
        return pickle.dumps(self)
