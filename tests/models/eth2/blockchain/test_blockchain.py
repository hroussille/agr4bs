"""
    Test suite for the Blockchain class
"""

from agr4bs.models.eth2.blockchain import Block, Blockchain, Attestation


def test_blockchain_properties():
    """
        Test that Blockchain class expose the right properties
    """
    genesis = Block(None, None, 0, [])
    blockchain = Blockchain(genesis)

    assert blockchain.genesis == genesis
    assert blockchain.head == genesis

def test_blockchain_justify_block():
    """
        Test that blockchain.justify_block() behaves correctly
    """
    genesis = Block(None, None, 0, [])
    block1 = Block(genesis.hash, None, 0, [])
    block2 = Block(block1.hash, None, 0, [])
    block3 = Block(block2.hash, None, 0, [])
    block4 = Block(block3.hash, None, 0, [])

    blockchain = Blockchain(genesis)

    blockchain.add_block(block1)
    blockchain.add_block(block2)
    blockchain.add_block(block3)
    blockchain.add_block(block4)

    assert block1.justified is False
    assert block2.justified is False
    assert block3.justified is False
    assert block4.justified is False

    blockchain.justify_block(block4)

    assert block1.justified is True
    assert block2.justified is True
    assert block3.justified is True
    assert block4.justified is True

def test_blockchain_finalize_block():
    """
        Test that blockchain.finalize_block() behaves correctly
    """
    genesis = Block(None, None, 0, [])
    block1 = Block(genesis.hash, None, 1, [])
    block2 = Block(block1.hash, None, 2, [])
    block3 = Block(block2.hash, None, 3, [])
    block4 = Block(block3.hash, None, 4, [])

    blockchain = Blockchain(genesis)

    blockchain.add_block(block1)
    blockchain.add_block(block2)
    blockchain.add_block(block3)
    blockchain.add_block(block4)

    assert block1.finalized is False
    assert block2.finalized is False
    assert block3.finalized is False
    assert block4.finalized is False

    blockchain.finalize_block(block4)

    assert block1.finalized is True
    assert block2.finalized is True
    assert block3.finalized is True
    assert block4.finalized is True


def test_blockchain_last_justified_block():
    """
        Test that blockchain.get_last_justified_block() behaves correctly
    """
    genesis = Block(None, None, 0, [])
    blockchain = Blockchain(genesis)

    assert blockchain.get_last_justified_block() == genesis

    new_block = Block(genesis.hash, None, 0, [])
    blockchain.add_block(new_block)
    blockchain.head = new_block

    assert blockchain.get_last_justified_block() == genesis

    new_block.justified = True

    assert blockchain.get_last_justified_block() == new_block

def test_blockchain_last_finalized_block():
    """
        Test that blockchain.get_last_finalized_block() behaves correctly
    """
    genesis = Block(None, None, 0, [])
    blockchain = Blockchain(genesis)

    assert blockchain.get_last_finalized_block() == genesis

    new_block = Block(genesis.hash, None, 0, [])
    new_block.finalized = True
    blockchain.add_block(new_block)
    blockchain.head = new_block

    assert blockchain.get_last_finalized_block() == new_block

def test_blockchain_add_block_extending_main_chain():
    """
        Test that blockchain.add_block() behaves correctly when a new block
        extends the main chain
    """
    genesis = Block(None, None, 0, [])
    blockchain = Blockchain(genesis)

    assert blockchain.head == genesis

    block = Block(genesis.hash, "agent0", 0, [])
    blockchain.add_block(block)

    assert blockchain.head == block

def test_blockchain_add_block_extending_side_chain():
    """
        Test that blockchain.add_block() behaves correctly when a new block
        extends a side chain
    """
    genesis = Block(None, None, 0, [])
    blockchain = Blockchain(genesis)

    assert blockchain.head == genesis

    block = Block(genesis.hash, "agent0", 0, [])
    block1 = Block(block.hash, "agent0", 0, [])
    block2 = Block(block.hash, "agent0", 0, [])

    blockchain.add_block(block)
    blockchain.add_block(block1)
    blockchain.add_block(block2)

    assert blockchain.head == block1


def test_blockchain_get_checkpoint_from_epoch_nominal_case():
    """
        Test that blockchain.get_checkpoint_from_epoch() behaves correctly
        in the nonminimal case where all slots have a single block
    """
    slot = 0

    genesis = Block(None, None, slot, [])
    blockchain = Blockchain(genesis)
    blocks = []
    previous = genesis

    for i in range(1, 33):
        block = Block(previous.hash, None, i, [])
        blockchain.add_block(block)
        blocks.append(block)
        previous = block

    assert blockchain.head == blocks[-1]
    assert blockchain.get_checkpoint_from_epoch(0) == genesis
    assert blockchain.get_checkpoint_from_epoch(1) == blocks[-1]



def test_blockchain_get_checkpoint_from_epoch_missing_blocks():
    """
        Test that blockchain.get_checkpoint_from_epoch() behaves correctly
        in the nonminimal case where all slots have a single block
    """
    slot = 0

    genesis = Block(None, None, slot, [])
    blockchain = Blockchain(genesis)
    

    # Add block in slot 33, ommitting 1 to 32
    block = Block(genesis.hash, None, 33, [])
    blockchain.add_block(block)

    assert blockchain.get_checkpoint_from_epoch(0) == genesis
    assert blockchain.get_checkpoint_from_epoch(1) == genesis
