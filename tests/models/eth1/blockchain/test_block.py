
"""
    Test suite for the Block class
"""

import pytest
from agr4bs.models.eth1.blockchain import Block, Transaction


def test_block_properties():
    """
        Test that Block class exposes the right properties
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", [tx])

    assert block.parent_hash == "genesis"
    assert block.creator == "agent0"
    assert block.transactions == [tx]
    assert block.height == 0

    with pytest.raises(ValueError) as excinfo:
        block.height = -1

    assert "Block height cannot be negative" in str(
        excinfo.value)


def test_block_total_fees():
    """
        Test that a Block total fee is computed correctly
    """
    tx1 = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    tx2 = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", [tx1, tx2])

    assert block.total_fees == 2


def test_block_hash():
    """
        Test that a Block hash is computed correctly (SHA256)
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", [tx])
    assert block.hash == "aa30b882730a7b9b545bff4c633a16afb7ea4e7f356fa5d505c056c13d821ffa"



def test_block_serialization():
    """
        Test that a Block serialization matches its content
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", [tx])

    serialized = block.serialize()

    deserialized = Block.from_serialized(serialized)
    assert deserialized == block
