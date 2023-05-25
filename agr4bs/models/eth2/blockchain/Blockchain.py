
"""
    Blockchain file class implementation
"""

import random
from collections import deque, defaultdict
from ....blockchain import IBlockchain
from .block import Block
from .attestation import Attestation


class Blockchain(IBlockchain):

    """
        Blockchain class implementation :

        A Blockchain is an ordered set of Blocks each linked to its parent.
        The Blockchain class keep tracks of known blocks, and maintains the
        main chain (i.e., the chain between the genesis Block and the head Block)
        according to some predefined rules.
    """

    def __init__(self, genesis: Block) -> None:
        super().__init__(genesis)

        self.slots_to_blocks = defaultdict(lambda: [])
        self.slots_to_blocks[genesis.slot].append(genesis)
        self.weights = defaultdict(lambda: 0)

        # Finalize genesis block by default
        self._blocks[genesis.hash].justified = True
        self._blocks[genesis.hash].finalized = True

        self.last_justified_block = genesis
        self.last_finalized_block = genesis

    def get_last_finalized_block(self) -> Block:
        """
            Get the last known finalized block
        """
        last_finalized = None
        current = self._head

        while current is not None:
            if current.finalized:
                last_finalized = current
                break

            current = self._blocks[current.parent_hash]

        return last_finalized
    
    def get_blocks_for_slot(self, slot: int) -> list[Block]:
        """
            Get the list of blocks for a given slot
        """
        return self.slots_to_blocks[slot]
    
    def get_last_justified_block(self) -> Block:
        """
            Get the last known justified block
        """
        last_justified = None
        current = self._head
        i = 0

        while current is not None:
            if current.justified is True:
                last_justified = current
                break

            i = i + 1

            current = self._blocks[current.parent_hash]

        return last_justified

    def get_finalized_chain(self) -> list[Block]:
        """ Get the current finalized chain

            :returns: The list of Blocks constituting the finalized chain
            :rtype: list[Block]
        """
        chain = deque()
        current = self.get_last_finalized_block()

        while current is not None:
            chain.appendleft(current)
            current = self._blocks[current.parent_hash]

        return list(chain)
    
    def justify_block(self, block: Block) -> None:
        """ Justify a block

            :param block: The block to justify
            :type block: Block
        """
        current = block

        if current is not None and current.justified is False:
            self.last_justified_block = current

        # Justify the block and all its ancestors
        while current is not None and current.justified is False:
            current.justified = True
            current = self._blocks[current.parent_hash]

    def finalize_block(self, block: Block) -> None:
        """ Finalize a block

            :param block: The block to finalize
            :type block: Block
        """
        current = block

        if current is not None and current.finalized is False:
            self.last_finalized_block = current

        # Finalize the block and all its ancestors
        while current is not None and current.finalized is False:
            current.justified = True
            current.finalized = True
            current = self._blocks[current.parent_hash]

    def contains_attestation(self, attestation: Attestation) -> bool:
        """ Check if the blockchain contains the given attestation

            :param attestation: The attestation to check
            :type attestation: Attestation
            :returns: True if the attestation is known, False otherwise
            :rtype: bool
        """
        return False
    
    def process_block_votes(self, attestations: list[Attestation]) -> tuple[list[Block], list[Block]]:
        """ Process a list of attestations

            :param attestations: The list of attestations to process
            :type attestations: list[Attestation]
        """
    
        weights = defaultdict(lambda: 0)
        previous_head = self._head

        parent = self.last_justified_block
        subchains = {}

        if parent is None:
            parent = self.genesis

        # Gather all the subchains from the attestations
        # Only one subchain fetch is necessary per batch of attestations
        # All subsequent attestations with the same root will have the same subchain
        for attestation in attestations:

            block = self.get_block(attestation.root)

            # Block not known, or comes from an outtaded view of the chain : discard the block vote
            if block is None or block.slot < parent.slot:
                continue

            if weights[block.hash] > 0:
                weights[block.hash] += 1
                continue

            subchain = self.get_subchain(block, parent, include_child=True, include_parent=True)

            if len(subchain) == 0:
                raise ValueError("Received an attestation not extending the current finalized chain")

            weights[block.hash] = 1
            subchains[block.hash] = subchain
            
        for subchain in subchains.values():
            for block in subchain: 
                if (block.hash not in weights):
                    weights[block.hash] = 1
                else:
                    weights[block.hash] += 1
                    
        # Walk through the weights starting from the last justified block
        current = parent

        while self._children[current.hash] is not None:

            childrens = self._children[current.hash]

            # No children, we are done
            if len(childrens) == 0:
                break

            # Fast forward if there is only one child
            if len(childrens) == 1:
                current = childrens[0]
                continue

            children_weights = [weights[child.hash] for child in childrens]
            #max_weight = max(children_weights)

            sorted_children = sorted(childrens, key=lambda child: (weights[child.hash], child.hash), reverse=True)
            current = sorted_children[0]

            # TODO: fix for selection on block hash
            # current = random.choice([child for child in childrens if weights[child.hash] == max_weight])

        # Update the head block
        self._head = current
        self.weights = weights[current.hash]

        reverted_blocks = []
        appended_blocks = []

        if self._head == previous_head:
            return reverted_blocks, appended_blocks
        
        reverted_blocks, appended_blocks = self.find_path(previous_head, self._head)

        return reverted_blocks, appended_blocks

    
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

        if block.height == self._head.height and random.randoadd_blockm() > 0.5:
            return True

        return False

    def get_checkpoint_from_epoch(self, epoch: int) -> Block:
        """
            Get the checkpoint for a given epoch according to the local chain
        """

        if epoch == 0:
            return self.genesis
        
        slot = epoch * 32

        while True:
            slot_blocks = self.slots_to_blocks[slot]

            # We may have multiple blocks for the same slot : we return the one on the main chain
            for block in slot_blocks:
                if self.is_block_on_main_chain(block):
                    return block
                
            # We did not find any block for this slot on the main chain, we try the previous slot
            slot -= 1
    
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

        # Update the head block if the new block extends the current head
        if block.parent_hash == self._head.hash:
            self._head = block

        self.slots_to_blocks[block.slot].append(block)

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

        # If we extend the main chain : update the head
        if self.is_close_parent(self._head, previous_head, len(added_blocks)):
            appended_blocks = self.get_subchain(self._head, previous_head)

        return True, reverted_blocks, appended_blocks
