
"""
    Blockchain file class implementation
"""

from collections import defaultdict, deque
from .block import IBlock


class IBlockchain():

    """
        Blockchain class implementation :

        A Blockchain is an ordered set of Blocks each linked to its parent.
        The Blockchain class keep tracks of known blocks, and maintains the
        main chain (i.e., the chain between the genesis Block and the head Block)
        according to some predefined rules.
    """

    def __init__(self, genesis: IBlock) -> None:

        genesis.compute_hash()
        self._genesis = genesis
        self._blocks = defaultdict(lambda: None)
        self._staging_blocks = defaultdict(lambda: [])
        self._blocks[genesis.hash] = genesis
        self._children = defaultdict(lambda: [])
        self._head = self._genesis

        # TODO: add an internal nonce to avoid hash conflich when similar data are contained ?

    def get_block(self, _hash: str) -> IBlock:
        """ Get a specific block by its hash

            :param _hash: the hash of the Block to retrieve
            :type _hash: str
            :returns: the Block with the corresponding hash or None
            :rtype: Block
        """
        if _hash in self._blocks:
            return self._blocks[_hash]

        return None

    def get_chain(self) -> list[IBlock]:
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
    def genesis(self) -> IBlock:
        """ Get the genesis Block of the Blockchain

            :returns: The genesis Block
            :rtype: Block
        """
        return self._genesis

    @property
    def head(self) -> IBlock:
        """ Get the head Block of the Blockchain

            :returns: The head Block
            :rtype: Block
        """
        return self._head

    @head.setter
    def head(self, new_head: IBlock):
        """ Set the head Block of the Blockchain

        :param new_head: the new head
        :type new_head: Block
        """

        if self.get_block(new_head.hash) is None:
            raise ValueError("Setting head with an uknown block")

        if new_head.invalid:
            raise ValueError("Setting head with an invalid block")

        self._head = new_head

    def is_block_on_main_chain(self, block: IBlock) -> bool:
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

    def find_new_head(self) -> IBlock:
        """
            Find the new head in the blockchain
            TODO: optimize this
        """
        raise NotImplementedError;

    def get_subchain(self, child: IBlock, parent: IBlock, include_child=True, include_parent=False) -> bool:
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
                
                current = self._head

                while True:

                    if (current.hash == self.genesis.hash):
                        break

                    current = self._blocks[current.parent_hash]

                raise ValueError("Not path between blocks")

        if include_parent:
            path.appendleft(parent)

        return list(path)

    def is_close_parent(self, child_block: IBlock, parent_block: IBlock, limit=10) -> bool:
        """
            Find out if a Block is a distant parent of another Block
        """

        # Special case if child == parent
        if child_block.hash == parent_block.hash:
            return True

        for _ in range(limit):

            if child_block.parent_hash == parent_block.hash:
                return True

            if child_block.parent_hash is not None:
                child_block = self._blocks[child_block.parent_hash]
            else:
                return False

        return False

    def get_nth_parent(self, block: IBlock, n: int) -> IBlock:
        """
            Get the nth parent of a given Block.
            Stops at genesis block.
        """

        for _ in range(n):
            if block.parent_hash is not None:
                block = self._blocks[block.parent_hash]

        return block

    def get_children(self, block: IBlock) -> list[IBlock]:
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

    def find_common_ancestor(self, block_a: IBlock, block_b: IBlock) -> IBlock:
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

    def find_path(self, block_a: IBlock, block_b: IBlock) -> tuple[list[IBlock], list[IBlock]]:
        """
            Find a path from block_a to block_b in the chain
        """
        common_ancestor = self.find_common_ancestor(block_a, block_b)
        reverted_blocks = self.get_subchain(block_a, common_ancestor)
        appended_blocks = self.get_subchain(block_b, common_ancestor)

        return reverted_blocks, appended_blocks

    def add_block_strict(self, block: IBlock) -> bool:
        """ Add a Block to the Blockchain in Strict Mode

            Strict Mode only allows the inclusion of a new Block if its
            parent Block is already known and included in the Blockchain.

            Rejected Blocks ARE NOT included in the staging area.

            :param block: The Block to add to the Blockchain
            :type block: Block
            :returns: wether the Block was added to the chain or not
            :rtype: bool
        """
        raise NotImplementedError

    def mark_invalid(self, block: IBlock):
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

    def add_block(self, block: IBlock) -> tuple[bool, list[IBlock], list[IBlock]]:
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
        raise NotImplementedError
