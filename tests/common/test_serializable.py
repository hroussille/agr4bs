
"""
    Test suite for the Serializable class
"""

from agr4bs.common import Serializable


def test_serialization():
    """
        Test that serialization yields bytes
    """
    serializable = Serializable()
    serialized = serializable.serialize()

    assert isinstance(serialized, bytes)


def test_deserialization():
    """
        Test that deserialization yields an object of the correct type
    """
    serializable = Serializable()
    serialized = serializable.serialize()

    deserialized = Serializable.from_serialized(serialized)
    assert isinstance(deserialized, Serializable)
