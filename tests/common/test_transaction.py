"""
    Test suite for the Transaction class
"""

from agr4bs import Payload, Transaction


def test_tx_no_payload():
    """
    Ensures that a tx can be created with no Payload
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", amount=1000, fee=1)
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1

    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload:  }"


def test_tx_with_empty_payload():
    """
    Ensures that a tx can be created with an empty Payload
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", amount=1000, fee=1, payload=Payload())
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1
    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload:  }"


def test_tx_with_payload():
    """
    Ensures that a tx can be created with a non empty Paylaod
    Ensures serialization validity
    """
    tx = Transaction("agent0", "agent1", amount=1000,
                     fee=1, payload=Payload("deadbeef"))
    assert tx.origin == "agent0"
    assert tx.to == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1
    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload: deadbeef }"
