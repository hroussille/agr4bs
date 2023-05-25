
"""
    Test suite for the Block class
"""

import pytest
from agr4bs import IBlock, ITransaction


def test_block_properties():
    """
        Test that Block class exposes the right properties
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000, fee=1)
    block = IBlock("genesis", "agent0", [tx])

    assert block.parent_hash == "genesis"
    assert block.creator == "agent0"
    assert block.transactions == [tx]
    assert block.height == 0

    with pytest.raises(ValueError) as excinfo:
        block.height = -1

    assert "Block height cannot be negative" in str(
        excinfo.value)


def test_block_hash():
    """
        Test that a Block hash is computed correctly (SHA256)
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000, fee=1)
    block = IBlock("genesis", "agent0", [tx])
    assert block.hash == "c7634fed0225a3e84f38d8c7321cd891500c6962376babea3f0dec80964557a7"


def test_block_serialization():
    """
        Test that a Block serialization matches its content
    """
    tx = ITransaction("agent0", "agent1", 0, value=1000, fee=1)
    block = IBlock("genesis", "agent0", [tx])

    serialized = block.serialize()

    deserialized = IBlock.from_serialized(serialized)
    assert deserialized == block
