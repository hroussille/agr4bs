from agr4bs.Common import Transaction, Block, Blockchain


def test_Blockchain_properties():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    assert blockchain.genesis == genesis
    assert blockchain.head == genesis


def test_Blockchain_add_block_strict():

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


def test_Blockchain_add_block_strict_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.add_block(block1) is True
    assert blockchain.head == block1
    assert blockchain.get_block(block1.hash).height == 1

    assert blockchain.add_block(block2) is True
    assert blockchain.head == block2
    assert blockchain.get_block(block2.hash).height == 2

    assert blockchain.add_block(block3) is True
    assert blockchain.head == block3
    assert blockchain.get_block(block3.hash).height == 3

    assert blockchain.add_block(block4) is False
    assert blockchain.head == block3

    assert blockchain.genesis == genesis
    assert blockchain.get_block(block4.hash) is None


def test_Blockchain_add_block_wrong_order_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.add_block(block3) is False
    assert blockchain.head == genesis

    assert blockchain.add_block(block2) is False
    assert blockchain.head == genesis

    assert blockchain.add_block(block1) is True
    assert blockchain.head == block3

    assert blockchain.get_block(block1.hash).height == 1
    assert blockchain.get_block(block2.hash).height == 2
    assert blockchain.get_block(block3.hash).height == 3

    assert blockchain.add_block(block4) is False
    assert blockchain.get_block(block4.hash) is None

    assert blockchain.genesis == genesis

    for key in blockchain._staging_blocks:
        assert key == "uknown hash"


def test_Blockchain_add_block_fork_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])

    # TODO: add an internal nonce to avoid hash conflich when similar data are contained
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.add_block(block1) is True
    assert blockchain.head == block1

    assert blockchain.add_block(block2) is True
    assert blockchain.head == block2

    assert blockchain.add_block(block3) is True
    assert blockchain.head == block3

    assert blockchain.add_block(block4) is True
    assert blockchain.head == block3 or blockchain.head == block4

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    assert len(blockchain._staging_blocks.keys()) == 0


def test_Blockchain_add_block_fork_wrong_order_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])

    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.add_block(block4) is False
    assert blockchain.head == genesis

    assert blockchain.add_block(block3) is False
    assert blockchain.head == genesis

    assert blockchain.add_block(block1) is True
    assert blockchain.head == block1

    assert blockchain.add_block(block2) is True
    assert blockchain.head == block3 or blockchain.head == block4

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    assert len(blockchain._staging_blocks.keys()) == 0
