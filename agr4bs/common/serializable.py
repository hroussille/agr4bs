
"""
    Serializable file class implementation
"""

import pickle


class Serializable:

    """
        A Serializable can be serialized to a pickle byte array.
    """

    def serialize(self) -> bytes:
        """
            Serialize the current object
        """
        return pickle.dumps(self)

    @classmethod
    def from_serialized(cls, serialized: str) -> 'Serializable':
        """
            Rebuilds a Block from a serialized Block
        """
        deserialized = pickle.loads(serialized)

        if not isinstance(deserialized, cls):
            return None

        return deserialized
