from agr4bs.Common import Transaction, Payload


def test_tx_no_payload():

    tx = Transaction("agent0", "agent1", amount=1000, fee=1)
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1

    print(tx.serialize())
    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload:  }"


def test_tx_with_empty_payload():

    tx = Transaction("agent0", "agent1", amount=1000, fee=1, payload=Payload())
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1
    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload:  }"


def test_tx_with_payload():

    tx = Transaction("agent0", "agent1",  amount=1000,
                     fee=1, payload=Payload("deadbeef"))
    assert tx.origin == "agent0"
    assert tx.destination == "agent1"
    assert tx.amount == 1000
    assert tx.fee == 1
    assert tx.serialize(
    ) == "{ from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload: deadbeef }"
