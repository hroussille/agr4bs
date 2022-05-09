from agr4bs.Common import Transaction, Block, Blockchain


def test_Blockchain_properties():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    assert blockchain.genesis == genesis
    assert blockchain.head == genesis


def test_Blockchain_addBlockStrict():

    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.addBlockStrict(block1) == True
    assert blockchain.head == block1
    assert blockchain.getBlock(block1.hash).height == 1

    assert blockchain.addBlockStrict(block2) == True
    assert blockchain.head == block2
    assert blockchain.getBlock(block2.hash).height == 2

    assert blockchain.addBlockStrict(block3) == True
    assert blockchain.head == block3
    assert blockchain.getBlock(block3.hash).height == 3

    assert blockchain.addBlockStrict(block4) == False
    assert blockchain.head == block3
    assert blockchain.getBlock(block4.hash) == None

    assert blockchain.genesis == genesis


def test_Blockchain_addBlock_strict_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.addBlock(block1) == True
    assert blockchain.head == block1
    assert blockchain.getBlock(block1.hash).height == 1

    assert blockchain.addBlock(block2) == True
    assert blockchain.head == block2
    assert blockchain.getBlock(block2.hash).height == 2

    assert blockchain.addBlock(block3) == True
    assert blockchain.head == block3
    assert blockchain.getBlock(block3.hash).height == 3

    assert blockchain.addBlock(block4) == False
    assert blockchain.head == block3

    assert blockchain.genesis == genesis
    assert blockchain.getBlock(block4.hash) == None


def test_Blockchain_addBlock_wrong_order_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block("uknown hash", "agent0", [])

    assert blockchain.addBlock(block3) == False
    assert blockchain.head == genesis

    assert blockchain.addBlock(block2) == False
    assert blockchain.head == genesis

    assert blockchain.addBlock(block1) == True
    assert blockchain.head == block3

    assert blockchain.getBlock(block1.hash).height == 1
    assert blockchain.getBlock(block2.hash).height == 2
    assert blockchain.getBlock(block3.hash).height == 3

    assert blockchain.addBlock(block4) == False
    assert blockchain.getBlock(block4.hash) == None

    assert blockchain.genesis == genesis

    for key in blockchain._stagingBlocks:
        assert key == "uknown hash"


def test_Blockchain_addBlock_fork_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])

    # TODO: add an internal nonce to avoid hash conflich when similar data are contained
    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.addBlock(block1) == True
    assert blockchain.head == block1

    assert blockchain.addBlock(block2) == True
    assert blockchain.head == block2

    assert blockchain.addBlock(block3) == True
    assert blockchain.head == block3

    assert blockchain.addBlock(block4) == True
    assert blockchain.head == block3 or blockchain.head == block4

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    assert len(blockchain._stagingBlocks.keys()) == 0


def test_Blockchain_addBlock_fork_wrong_order_scenario():
    genesis = Block(None, None, [])
    blockchain = Blockchain(genesis)

    block1 = Block(genesis.hash, "agent0", [])
    block2 = Block(block1.hash, "agent0", [])

    block3 = Block(block2.hash, "agent0", [])
    block4 = Block(block2.hash, "agent1", [])

    assert blockchain.addBlock(block4) == False
    assert blockchain.head == genesis

    assert blockchain.addBlock(block3) == False
    assert blockchain.head == genesis

    assert blockchain.addBlock(block1) == True
    assert blockchain.head == block1

    assert blockchain.addBlock(block2) == True
    assert blockchain.head == block3 or blockchain.head == block4

    assert blockchain.genesis == genesis
    assert block3.height == block4.height == 3

    assert len(blockchain._stagingBlocks.keys()) == 0
