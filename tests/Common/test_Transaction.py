from agr4bs.Common import Transaction, Payload


def test_tx_no_payload():

    tx = Transaction("agent0", "agent1", 1000)
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.serialize() == "{ agent0 - agent1 - 0000001000 -  }"


def test_tx_with_empty_payload():

    tx = Transaction("agent0", "agent1", 1000, Payload())
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.serialize() == "{ agent0 - agent1 - 0000001000 -  }"


def test_tx_with_payload():

    tx = Transaction("agent0", "agent1", 1000, Payload("deadbeef"))
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.serialize() == "{ agent0 - agent1 - 0000001000 - deadbeef }"
