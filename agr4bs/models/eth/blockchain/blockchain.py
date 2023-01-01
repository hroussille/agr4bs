
"""
    Blockchain file class implementation
"""

import random
from collections import defaultdict, deque
from .block import Block


class Blockchain():

    """
        Blockchain class implementation :

        A Blockchain is an ordered set of Blocks each linked to its parent.
        The Blockchain class keep tracks of known blocks, and maintains the
        main chain (i.e., the chain between the genesis Block and the head Block)
        according to some predefined rules.
    """

    def __init__(self, genesis: Block) -> None:

        genesis.compute_hash()
        self._genesis = genesis
        self._blocks = defaultdict(lambda: None)
        self._staging_blocks = defaultdict(lambda: [])
        self._blocks[genesis.hash] = genesis
        self._children = defaultdict(lambda: [])
        self._head = self._genesis

        # TODO: add an internal nonce to avoid hash conflich when similar data are contained ?

    def get_block(self, _hash: str) -> Block:
        """ Get a specific block by its hash

            :param _hash: the hash of the Block to retrieve
            :type _hash: str
            :returns: the Block with the corresponding hash or None
            :rtype: Block
        """
        if _hash in self._blocks:
            return self._blocks[_hash]

        return None

    def get_chain(self) -> list[Block]:
        """ Get the current main chain

            :returns: The list of Blocks constituting the main chain
            :rtype: list[Block]
        """
        chain = deque()
        current = self._head

        while current is not None:
            chain.appendleft(current)
            current = self._blocks[current.parent_hash]

        return list(chain)

    @property
    def genesis(self) -> Block:
        """ Get the genesis Block of the Blockchain

            :returns: The genesis Block
            :rtype: Block
        """
        return self._genesis

    @property
    def head(self) -> Block:
        """ Get the head Block of the Blockchain

            :returns: The head Block
            :rtype: Block
        """
        return self._head

    @head.setter
    def head(self, new_head: Block):
        """ Set the head Block of the Blockchain

        :param new_head: the new head
        :type new_head: Block
        """

        if self.get_block(new_head.hash) is None:
            raise ValueError("Setting head with an uknown block")

        if new_head.invalid:
            raise ValueError("Setting head with an invalid block")

        self._head = new_head

    def is_block_on_main_chain(self, block: Block) -> bool:
        """ Check wether a Block is part of the main chain or not

            :param block: The Block to check for
            :type block: Block
            :returns: wether the Block is included in the main chain or not
            :rtype: bool
        """
        if self.get_block(block.hash) is None:
            return False

        current = self._head

        while current is not None:
            if current.hash == block.hash:
                return True
            current = self.get_block(current.parent_hash)

        return False

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

    def get_subchain(self, child: Block, parent: Block, include_child=True, include_parent=False) -> bool:
        """
            Get the subchain between child and parent
        """
        path = deque()

        if include_child is True:
            path.appendleft(child)

        if child.hash != parent.hash:
            while child.parent_hash != parent.hash and child.parent_hash is not None:
                child = self._blocks[child.parent_hash]
                path.appendleft(self._blocks[child.hash])

            if child.parent_hash != parent.hash:
                raise ValueError("Not path between blocks")

        if include_parent:
            path.appendleft(parent)

        return list(path)

    def is_close_parent(self, child_block: Block, parent_block: Block, limit=10) -> bool:
        """
            Find out if a Block is a distant parent of another Block
        """
        for _ in range(limit):

            if child_block.parent_hash == parent_block.hash:
                return True

            if child_block.parent_hash is not None:
                child_block = self._blocks[child_block.parent_hash]
            else:
                return False

        return False

    def get_nth_parent(self, block: Block, n: int) -> Block:
        """
            Get the nth parent of a given Block.
            Stops at genesis block.
        """

        for _ in range(n):
            if block.parent_hash is not None:
                block = self._blocks[block.parent_hash]

        return block

    def get_children(self, block: Block) -> list[Block]:
        """
            Get all the children blocks from a given block
        """

        if self.get_block(block.hash) is None:
            return

        children = []
        decendency = [child for child in self._children[block.hash]]

        while len(decendency):
            child = decendency.pop(0)
            children.append(child)
            decendency = [*decendency, *self._children[child.hash]]

        return children

    def find_common_ancestor(self, block_a: Block, block_b: Block) -> Block:
        """
            Find the first common ancestor of block_a and block_b
            Worst case is assumed to be the genesis block
        """

        if block_a.height > block_b.height:
            block_a = self.get_nth_parent(
                block_a, block_a.height - block_b.height)
        else:
            block_b = self.get_nth_parent(
                block_b, block_b.height - block_a.height)

        while block_a.parent_hash is not None and block_b.parent_hash is not None:

            if block_a == block_b:
                return block_a

            block_a = self._blocks[block_a.parent_hash]
            block_b = self._blocks[block_b.parent_hash]

        if block_a == block_b and block_a == self.genesis:
            return self.genesis

        raise ValueError("Blocks have no common ancestor")

    def find_path(self, block_a: Block, block_b: Block) -> tuple[list[Block], list[Block]]:
        """
            Find a path from block_a to block_b in the chain
        """
        common_ancestor = self.find_common_ancestor(block_a, block_b)
        reverted_blocks = self.get_subchain(block_a, common_ancestor)
        appended_blocks = self.get_subchain(block_b, common_ancestor)

        return reverted_blocks, appended_blocks

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

    def mark_invalid(self, block: Block):
        """
            Mark a block and all its descendent as invalid
        """

        if self.get_block(block.hash) is None:
            return False

        block.invalid = True

        children = self.get_children(block)

        for child in children:
            child.invalid = True

        return self._head.invalid

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
