"""
    Test suite for the Transaction class
"""

import pickle
from agr4bs import Payload, Transaction


def test_tx_no_payload():
    """
    Ensures that a tx can be created with no Payload
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1

    serialized = tx.serialize()

    assert serialized == pickle.dumps(tx)

    deserialized = Transaction.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == tx.hash


def test_tx_with_empty_payload():
    """
    Ensures that a tx can be created with an empty Payload
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000,
                     fee=1, payload=Payload())
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1

    serialized = tx.serialize()

    assert serialized == pickle.dumps(tx)

    deserialized = Transaction.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == tx.hash


def test_tx_with_payload():
    """
    Ensures that a tx can be created with a non empty Paylaod
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000,
                     fee=1, payload=Payload(b"deadbeef"))
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1

    serialized = tx.serialize()

    assert serialized == pickle.dumps(tx)

    deserialized = Transaction.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == tx.hash
