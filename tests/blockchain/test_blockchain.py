"""
    Test suite for the Blockchain class
"""

from agr4bs import IBlock, IBlockchain


def test_blockchain_properties():
    """
        Test that Blockchain class expose the right properties
    """
    genesis = IBlock(None, None, [])
    blockchain = IBlockchain(genesis)

    assert blockchain.genesis == genesis
    assert blockchain.head == genesis
