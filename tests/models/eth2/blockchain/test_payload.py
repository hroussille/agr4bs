"""
    Test suite for the Transaction class
"""

import pytest
from agr4bs import Payload


def test_payload_data():
    """
        Test Payload data integrity
    """
    payload = Payload(b"deadbeef")
    assert payload.data == b"deadbeef"


def test_payload_data_type():
    """
        Test Exception on invalid Payload data type
    """
    with pytest.raises(TypeError) as excinfo:
        Payload(1)

    assert "Invalid Payload data type. Got <class 'int'> expected <class 'bytes'>" in str(
        excinfo.value)


def test_payload_serialization():
    """
        Test Payload serialization
    """

    data = b"deadbeed"

    payload = Payload(data)
    serialized = payload.serialize()

    assert Payload.from_serialized(serialized) == payload
