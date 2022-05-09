from typing import Type
import pytest
from agr4bs.Common import Payload


def test_Payload_data():

    payload = Payload("deadbeef")
    assert(payload.data == "deadbeef")


def test_Payload_data_type():

    with pytest.raises(TypeError) as excinfo:
        payload = Payload(1)

    print(excinfo.value)
    assert "Invalid Payload data type. Got <class 'int'> expected str" in str(
        excinfo.value)


def test_Payload_serialization():

    payload1 = Payload("deadbeef")
    payload2 = Payload("")

    assert(payload1.serialize() == "deadbeef")
    assert(payload2.serialize() == "")
