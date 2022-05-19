
"""
    Test suite for the Block class
"""

import pickle
import pytest
from agr4bs import Block, Transaction


def test_block_properties():
    """
        Test that Block class exposes the right properties
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
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
    tx1 = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
    tx2 = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx1, tx2])

    assert block.total_fees == 2


def test_block_hash():
    """
        Test that a Block hash is computed correctly (SHA256)
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx])
    assert block.hash == "90f6a969498735e6cba454ea16f3283222dc614e8c5b75c9a7c845609b0bfbe0"


def test_block_serialization():
    """
        Test that a Block serialization matches its content
    """
    tx = Transaction("agent0", "agent1", 0, amount=1000, fee=1)
    block = Block("genesis", "agent0", [tx])

    serialized = block.serialize()

    assert serialized == pickle.dumps(block)

    deserialized = Block.from_serialized(serialized)

    assert deserialized is not None
    assert deserialized.compute_hash() == block.hash
