"""
    Test suite for the Transaction class
"""

import pickle
from agr4bs import Payload, ITransaction


def test_tx_no_payload():
    """
    Ensures that a tx can be created with no Payload
    Ensures serialization validity
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000, fee=1)
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.value == 1000
    assert tx.fee == 1

    serialized = tx.serialize()

    assert serialized == pickle.dumps(tx)

    deserialized = ITransaction.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == tx.hash


def test_tx_with_empty_payload():
    """
    Ensures that a tx can be created with an empty Payload
    Ensures serialization validity
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000,
                     fee=1, payload=Payload())
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.value == 1000
    assert tx.fee == 1

    serialized = tx.serialize()

    assert serialized == pickle.dumps(tx)

    deserialized = ITransaction.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == tx.hash


def test_tx_with_payload():
    """
    Ensures that a tx can be created with a non empty Paylaod
    Ensures serialization validity
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000,
                     fee=1, payload=Payload(b"deadbeef"))
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.value == 1000
    assert tx.fee == 1

    serialized = tx.serialize()
    deserialized = ITransaction.from_serialized(serialized)

    assert deserialized == tx
