import random
from .Block import Block
from collections import deque


class Blockchain(object):

    def __init__(self, genesis: Block) -> None:
        self._genesis = genesis
        self._head = self._genesis
        self._blocks = {}
        self._stagingBlocks = {}
        self._blocks[genesis.hash] = genesis
        # TODO: add an internal nonce to avoid hash conflich when similar data are contained ?

    def getBlock(self, hash: str) -> Block:
        if hash in self._blocks:
            return self._blocks[hash]
        return None

    def getChain(self) -> list[Block]:
        chain = deque()
        current = self._head

        while current != None:
            chain.appendleft(current)
            current = self._blocks[current.parent]

        return list(chain)

    @property
    def genesis(self) -> Block:
        return self._genesis

    @property
    def head(self) -> Block:
        return self._head

    def _unstageBlocks(self, block: Block) -> list[Block]:
        dependencies = [block]
        allUnstaged = []

        while len(dependencies) > 0:
            newDependencies = []
            for dependency in dependencies:
                if dependency.hash in self._stagingBlocks:
                    unstaged = [
                        stagedBlock for stagedBlock in self._stagingBlocks[dependency.hash]]
                    newDependencies = [*newDependencies, *unstaged]
                    del self._stagingBlocks[dependency.hash]
                    allUnstaged = [*allUnstaged, *unstaged]

            dependencies = newDependencies

        return list(allUnstaged)

    def _forkRule(self, block: Block):
        """ If block height is higher than head it becomes the new head 
            Else If block height is equal to head height : random choice
            Otherwise head is left unchanged
        """
        if block.height > self._head.height:
            self._head = block

        elif block.height == self._head.height:
            if random.random() > 0.5:
                self._head = block

    def addBlockStrict(self, block: Block):
        """ Do nothing if the block is already known """
        if block.hash in self._blocks:
            return False

        """ Strict mode : do nothing if parent is uknown """
        if block.parentHash not in self._blocks:
            return False

        block.height = self._blocks[block.parentHash].height + 1
        self._blocks[block.hash] = block
        self._forkRule(block)

        return True

    def addBlock(self, block: Block) -> bool:
        """ Attempt to add a block to the blockchain
        """

        """ Do nothing if the block is already known """
        if block.hash in self._blocks:
            return False

        """ Uknown parent : this may happen due to network delay / loss """
        if block.parentHash not in self._blocks:
            if block.parentHash not in self._stagingBlocks:
                self._stagingBlocks[block.parentHash] = [block]
            else:
                self._stagingBlocks[block.parentHash].append(block)
            return False

        block.height = self._blocks[block.parentHash].height + 1
        self._blocks[block.hash] = block
        self._forkRule(block)

        for dependentBlock in self._unstageBlocks(block):
            print(dependentBlock.hash)
            print(dependentBlock)
            if self.addBlockStrict(dependentBlock) is not True:
                raise ValueError("Chain is corrupted.")

        return True
