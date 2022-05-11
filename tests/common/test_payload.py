"""
    Test suite for the Transaction class
"""

import pytest
from agr4bs import Payload


def test_payload_data():
    """
        Test Payload data integrity
    """
    payload = Payload("deadbeef")
    assert payload.data == "deadbeef"


def test_payload_data_type():
    """
        Test Exception on invalid Payload data type
    """
    with pytest.raises(TypeError) as excinfo:
        Payload(1)

    assert "Invalid Payload data type. Got <class 'int'> expected str" in str(
        excinfo.value)


def test_payload_serialization():
    """
        Test Payload serialization
    """
    payload1 = Payload("deadbeef")
    payload2 = Payload("")

    assert payload1.serialize() == "deadbeef"
    assert payload2.serialize() == ""
