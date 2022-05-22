"""
    Test suite for the Blockchain class
"""

from agr4bs import Block, Blockchain


def test_blockchain_properties():
    """
        Test that Blockchain class expose the right properties
    """
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    assert blockchain.genesis == genesis
    assert blockchain.head == genesis


def test_blockchain_add_block_strict():
    """
        Test that Blockchain.add_block_strict() behaves correctly

        add_block_strict() should add a block and return true if its
        parent block is known, and included in the blockchain.

        add_block_struct() should not add a block and return false if
        its parent block is uknown or not included in the blockchain.

        Out of order blocks / Uknown parents MUST fail
    """

    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.add_block_strict(block1) is True
    assert blockchain.head == block1
    assert blockchain.get_block(block1.hash).height == 1

    assert blockchain.add_block_strict(block2) is True
    assert blockchain.head == block2
    assert blockchain.get_block(block2.hash).height == 2

    assert blockchain.add_block_strict(block3) is True
    assert blockchain.head == block3
    assert blockchain.get_block(block3.hash).height == 3

    assert blockchain.add_block_strict(block4) is False
    assert blockchain.head == block3
    assert blockchain.get_block(block4.hash) is None

    assert blockchain.genesis == genesis


def test_blockchain_add_block_in_strict_scenario():
    """
        Test that Blockchain.add_block() behaves as add_block_strict()
        in the same scenario as test_add_block_strict()
    """
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.add_block(block1) == tuple([True, [], [block1]])
    assert blockchain.head == block1
    assert blockchain.get_block(block1.hash).height == 1

    assert blockchain.add_block(block2) == tuple([True, [], [block2]])
    assert blockchain.head == block2
    assert blockchain.get_block(block2.hash).height == 2

    assert blockchain.add_block(block3) == tuple([True, [], [block3]])
    assert blockchain.head == block3
    assert blockchain.get_block(block3.hash).height == 3

    assert blockchain.add_block(block4) == tuple([False, [], []])
    assert blockchain.head == block3

    assert blockchain.genesis == genesis
    assert blockchain.get_block(block4.hash) is None


def test_blockchain_add_block_wrong_order_scenario():
    """
        Test that Blockchain.add_block() behaves correctly
        even if blocks are fed out of order.
    """
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.add_block(block3) == tuple([False, [], []])
    assert blockchain.head == genesis

    assert blockchain.add_block(block2) == tuple([False, [], []])
    assert blockchain.head == genesis

    assert blockchain.add_block(block1) == tuple(
        [True, [], [block1, block2, block3]])
    assert blockchain.head == block3

    assert blockchain.get_block(block1.hash).height == 1
    assert blockchain.get_block(block2.hash).height == 2
    assert blockchain.get_block(block3.hash).height == 3

    assert blockchain.add_block(block4) == tuple([False, [], []])
    assert blockchain.get_block(block4.hash) is None

    assert blockchain.genesis == genesis

    # pylint: disable=protected-access
    for key in blockchain._staging_blocks:
        assert key == "uknown hash"


def test_blockchain_add_block_fork_scenario():
    """
        Test that Blockchain.add_block() behaves correctly
        even in the case of a fork.
    """
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])

    # TODO: add an internal nonce to avoid hash conflich when similar data are contained
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.add_block(block1) == tuple([True, [], [block1]])
    assert blockchain.head == block1

    assert blockchain.add_block(block2) == tuple([True, [], [block2]])
    assert blockchain.head == block2

    assert blockchain.add_block(block3) == tuple([True, [], [block3]])
    assert blockchain.head == block3

    result = blockchain.add_block(block4)

    assert result == tuple([True, [], []]) or result == tuple(
        [True, [block3], [block4]])
    assert blockchain.head in [block3, block4]

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    # pylint: disable=protected-access
    assert len(blockchain._staging_blocks.keys()) == 0


def test_blockchain_add_block_fork_wrong_order_scenario():
    """
        Test that Blockchain.add_block() behaves correctly
        even in the case of a fork when blocks are fed out
        of order.
    """
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.add_block(block4) == tuple([False, [], []])
    assert blockchain.head == genesis

    assert blockchain.add_block(block3) == tuple([False, [], []])
    assert blockchain.head == genesis

    assert blockchain.add_block(block1) == tuple([True, [], [block1]])
    assert blockchain.head == block1

    result = blockchain.add_block(block2)

    assert result == tuple([True, [], [block2, block3]]) or result == tuple(
        [True, [], [block2, block4]])
    assert blockchain.head in [block3, block4]

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    # pylint: disable=protected-access
    assert len(blockchain._staging_blocks.keys()) == 0
