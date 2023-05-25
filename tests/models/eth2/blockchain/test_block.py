
"""
    Test suite for the Block class
"""

import pytest
from agr4bs.models.eth2.blockchain import Block, Transaction, Attestation


def test_block_properties():
    """
        Test that Block class exposes the right properties
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", 0, [tx])

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
    block = Block("genesis", "agent0", 0, [tx1, tx2])

    assert block.total_fees == 2

def test_block_hash():
    """
        Test that a Block hash is computed correctly (SHA256)
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", 0, [tx])
    assert block.hash == "3d51547d0b4e2110a85d5f8def82adecbb07ac8765ea7f850fac3d284c1ea22a"

def test_block_serialization():
    """
        Test that a Block serialization matches its content
    """
    tx = Transaction("agent0", "agent1", 0, value=1000, fee=1)
    block = Block("genesis", "agent0", 0, [tx])

    serialized = block.serialize()

    deserialized = Block.from_serialized(serialized)
    assert deserialized == block

def test_block_justified():
    """
        Test that a Block is justified correctly
    """
    block = Block("genesis", "agent0", 0, [])
    assert block.justified is False
    block.justified = True
    assert block.justified is True
    block.justified = False
    assert block.justified is False

def test_block_finalized():
    """
        Test that a Block is finalized correctly
    """
    block = Block("genesis", "agent0", 0, [])
    assert block.finalized is False
    block.finalized = True
    assert block.finalized is True
    block.finalized = False
    assert block.finalized is False

def test_block_attestations():
    """
        Test that a Block attestations are set correctly
    """

    block = Block("genesis", "agent0", 0, [])
    attestation = Attestation("agent_0", 0, 0, 0, "", "", "")

    assert isinstance(block.attestations, list)
    assert not block.attestations

    block.add_attestation(attestation)

    assert len(block.attestations) == 1
    assert attestation in block.attestations

def test_block_dupplicated_attestations():
    """
        Test that a Block doesn't accept dupplicated attestations for the same agent
    """
    
    block = Block("genesis", "agent0", 0, [])
    attestation = Attestation("agent_0", 0, 0, 0, "", "", "")

    assert isinstance(block.attestations, list)
    assert not block.attestations

    block.add_attestation(attestation)

    assert len(block.attestations) == 1
    assert attestation in block.attestations
    
    with pytest.raises(ValueError) as excinfo:
        block.add_attestation(attestation)
        assert excinfo.value == "Dupplicated attestation for agent0"
