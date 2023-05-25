
"""
    Blockchain file class implementation
"""

import random
from collections import defaultdict, deque
from ....blockchain import IBlockchain
from .block import Block


class Blockchain(IBlockchain):

    """
        Blockchain class implementation :

        A Blockchain is an ordered set of Blocks each linked to its parent.
        The Blockchain class keep tracks of known blocks, and maintains the
        main chain (i.e., the chain between the genesis Block and the head Block)
        according to some predefined rules.
    """

    def __init__(self, genesis: Block) -> None:
        super().__init__(genesis);

    def _unstage_blocks(self, block: Block) -> list[Block]:
        """ INTERNAL METHOD ONLY : DO NOT CALL IT EXTERNALLY

            Unstage all block dependant on block and cleanup the internal
            stagingBlocks data structure.

            When a Block is to be added to the Blockchain, but its parent is uknown,
            it will be placed in the staging area where it will wait until all of its
            depencies are met. This method retrieves all dependencies "recursively" and
            clear the appropriate parts of the staging area. The caller is expected to
            immediately add the returned Blocks.

            :param block: The Block for which dependencies should be made available
            :type block: Block
            :returns: The ordered list of dependant Blocks that can now be included
            :rtype: list[Block]
        """
        dependencies = [block]
        all_unstaged = []

        while len(dependencies) > 0:
            new_dependencies = []
            for dependency in dependencies:
                if dependency.hash in self._staging_blocks:
                    unstaged = self._staging_blocks[dependency.hash]
                    new_dependencies = [*new_dependencies, *unstaged]
                    del self._staging_blocks[dependency.hash]
                    all_unstaged = [*all_unstaged, *unstaged]

            dependencies = new_dependencies

        return list(all_unstaged)

    def find_new_head(self) -> Block:
        """
            Find the new head in the blockchain
            TODO: optimize this
        """

        sorted_blocks = [block for block in sorted(
            self._blocks.values(), key=lambda _block: _block.height, reverse=True)]
        candidate = next(block for block in sorted_blocks if not block.invalid)

        if self._is_new_head(candidate):
            return candidate

        return self._head

    def _is_new_head(self, block: Block) -> bool:
        """ INTERNAL METHOD ONLY : DO NOT CALL IT EXTERNALLY

            If block height is higher than head it becomes the new head
            Else If block height is equal to head height : random choice
            Otherwise head is left unchanged

            :param block: The block that may be elected as the new head
            :type block: Block
        """

        if block.invalid:
            raise ValueError("checking an invalid block for new head")

        if self._head.invalid:
            return True

        if block.height > self._head.height:
            return True

        if block.height == self._head.height and random.random() > 0.5:
            return True

        return False

    def add_block_strict(self, block: Block) -> bool:
        """ Add a Block to the Blockchain in Strict Mode

            Strict Mode only allows the inclusion of a new Block if its
            parent Block is already known and included in the Blockchain.

            Rejected Blocks ARE NOT included in the staging area.

            :param block: The Block to add to the Blockchain
            :type block: Block
            :returns: wether the Block was added to the chain or not
            :rtype: bool
        """

        if block.hash in self._blocks:
            return False

        if block.parent_hash not in self._blocks:
            return False

        block.height = self._blocks[block.parent_hash].height + 1
        block.invalid = self._blocks[block.parent_hash].invalid
        self._blocks[block.hash] = block

        if self._is_new_head(block):
            self._head = block

        return True

    def add_block(self, block: Block) -> tuple[bool, list[Block], list[Block]]:
        """ Add a Block to the Blockchain in non Strict mode

            Non Strict Mode allows the inclusion of a Block in the Blockchain
            if its parent Block is not already known and included in the Blockchain.
            It also process every dependencies and therefore may add more that 1
            Block on a single call

            Rejected Blocks ARE included in the staging area.

            :param block: The Block to add to the Blockchain
            :type block: Block
            :returns: wether the Block was added to the chain or not
            :rtype: bool
        """

        # Block is already known : exit early
        if block.hash in self._blocks:
            return False, [], []

        # Record the parent <-> child relation
        if block not in self._children[block.parent_hash]:
            self._children[block.parent_hash].append(block)

        # Parent is uknown : add the block to staging
        if block.parent_hash not in self._blocks and block.hash not in self._staging_blocks[block.parent_hash]:
            self._staging_blocks[block.parent_hash].append(block)
            return False, [], []

        previous_head = self._head
        added_blocks = [block, *self._unstage_blocks(block)]

        for added_block in added_blocks:
            if added_block.hash not in self._blocks:
                if self.add_block_strict(added_block) is not True:
                    raise ValueError("Chain is corrupted.")

        if self._head == previous_head:
            return (True, [], [])

        reverted_blocks = []
        appended_blocks = []

        # Best case scenario : extending the main chain
        if self.is_close_parent(self._head, previous_head, len(added_blocks)):
            appended_blocks = self.get_subchain(self._head, previous_head)

        # Worse case scenario : reorg
        else:
            reverted_blocks, appended_blocks = self.find_path(
                previous_head, self._head)

        return True, reverted_blocks, appended_blocks
