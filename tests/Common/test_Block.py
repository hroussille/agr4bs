import pytest
from agr4bs.Common import Transaction, Block


def test_Block_properties():
    tx = Transaction("agent0", "agent1", amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx])

    assert block.parentHash == "genesis"
    assert block.creator == "agent0"
    assert block.transactions == [tx]
    assert block.height == 0

    with pytest.raises(ValueError) as excinfo:
        block.height = -1

    assert "Block height cannot be negative" in str(
        excinfo.value)


def test_Block_totalFees():
    tx1 = Transaction("agent0", "agent1", amount=1000, fee=1)
    tx2 = Transaction("agent0", "agent1", amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx1, tx2])

    assert block.totalFees == 2


def test_Block_hash():
    tx = Transaction("agent0", "agent1", amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx])
    assert block.hash == "d9025bdb8668fcb32950d37fcf68e11858407adffe1b182b67d1126c8adc2b02"


def test_Block_serialization():
    tx = Transaction("agent0", "agent1", amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx])
    assert block.serialize(
    ) == "{ parentHash: genesis - creator: agent0 - transactions: { from: agent0 - to: agent1 - fee: 0000000001 - amount: 0000001000 - payload:  } }"
