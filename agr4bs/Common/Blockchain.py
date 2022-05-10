import random
from .Block import Block
from collections import deque


class Blockchain(object):

    def __init__(self, genesis: Block) -> None:
        self._genesis = genesis
        self._head = self._genesis
        self._blocks = {}
        self._staging_blocks = {}
        self._blocks[genesis.hash] = genesis
        # TODO: add an internal nonce to avoid hash conflich when similar data are contained ?

    def get_block(self, hash: str) -> Block:
        if hash in self._blocks:
            return self._blocks[hash]
        return None

    def get_chain(self) -> list[Block]:
        chain = deque()
        current = self._head

        while current is not None:
            chain.appendleft(current)
            current = self._blocks[current.parent_hash]

        return list(chain)

    def is_block_on_main_chain(self, block) -> bool:

        if self.get_block(block.hash) is None:
            return False

        current = self._head

        while current is not None:
            if current.hash == block.hash:
                return True
            current = self.get_block(current.parent_hash)

        return False

    @property
    def genesis(self) -> Block:
        return self._genesis

    @property
    def head(self) -> Block:
        return self._head

    def _unstage_blocks(self, block: Block) -> list[Block]:
        dependencies = [block]
        all_unstaged = []

        while len(dependencies) > 0:
            new_dependencies = []
            for dependency in dependencies:
                if dependency.hash in self._staging_blocks:
                    unstaged = [
                        stagedBlock for stagedBlock in self._staging_blocks[dependency.hash]]
                    new_dependencies = [*new_dependencies, *unstaged]
                    del self._staging_blocks[dependency.hash]
                    all_unstaged = [*all_unstaged, *unstaged]

            dependencies = new_dependencies

        return list(all_unstaged)

    def _fork_rule(self, block: Block):
        """ If block height is higher than head it becomes the new head
            Else If block height is equal to head height : random choice
            Otherwise head is left unchanged
        """
        if block.height > self._head.height:
            self._head = block

        elif block.height == self._head.height:
            if random.random() > 0.5:
                self._head = block

    def add_block_strict(self, block: Block):
        """ Do nothing if the block is already known """
        if block.hash in self._blocks:
            return False

        """ Strict mode : do nothing if parent is uknown """
        if block.parent_hash not in self._blocks:
            return False

        block.height = self._blocks[block.parent_hash].height + 1
        self._blocks[block.hash] = block
        self._fork_rule(block)

        return True

    def add_block(self, block: Block) -> bool:
        """ Attempt to add a block to the blockchain
        """

        """ Do nothing if the block is already known """
        if block.hash in self._blocks:
            return False

        """ Uknown parent : this may happen due to network delay / loss """
        if block.parent_hash not in self._blocks:
            if block.parent_hash not in self._staging_blocks:
                self._staging_blocks[block.parent_hash] = [block]
            else:
                self._staging_blocks[block.parent_hash].append(block)
            return False

        block.height = self._blocks[block.parent_hash].height + 1
        self._blocks[block.hash] = block
        self._fork_rule(block)

        for dependent_block in self._unstage_blocks(block):
            if self.add_block_strict(dependent_block) is not True:
                raise ValueError("Chain is corrupted.")

        return True
