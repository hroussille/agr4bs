
"""
BlockProposerContextChange:

The BlockProposerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

BlockProposer:

The BlockProposer implementation which MUST contain the following behaviors :
- select_transaction
- create_block
- propose_block
"""

import torch
from agr4bs.agents import ExternalAgent, ContextChange, AgentType
from agr4bs.events import CREATE_BLOCK
from agr4bs.network.messages import DiffuseBlock
from agr4bs.roles import Role, RoleType
from agr4bs.models.eth2.blockchain import Block, Transaction
from agr4bs.common import on, export

class MaliciousBlockProposerContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (BlockProposer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.transaction_selection_strategy = None
        self.malicious = True
        self.malicious_proposer = True


class MaliciousBlockProposer(Role):

    """
        Implementation of the BlockProposer Role which must
        expose the following behaviors :
        - select_transaction
        - create_block
        - propose_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        role_dependencies = [RoleType.BLOCKCHAIN_MAINTAINER]
        super().__init__(RoleType.BLOCK_PROPOSER, AgentType.EXTERNAL_AGENT, role_dependencies)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return MaliciousBlockProposerContextChange()

    @staticmethod
    @export
    def select_transactions(agent: ExternalAgent, pending_transactions: dict[list[Transaction]]) -> list[Transaction]:
        """ Select a subset of transactions for inclusion in a block

            :param transactions: the available transactions
            :type transactions: list[Transaction]
            :returns: the list of selected transactions
            :rtype: list[Transaction]
        """

        # Default selection strategy selects one pending transaction per account
        selected_transactions = []

        for account_pending in pending_transactions:
            selected_transactions.append(
                pending_transactions[account_pending][0])

        return selected_transactions

    @staticmethod
    @export
    @on(CREATE_BLOCK)
    def can_create_block(agent: ExternalAgent):
        """ Behavior called on CREATE_BLOCK event. This is a system event triggered
            by the Environment.

            It is a one time authorization to create and propose a new Block to the network.
        """
        blockchain = agent.context['blockchain']
        honest_head = blockchain.get_block(agent.get_head())
        current_attester_is_malicious = agent.context['current_attester_is_malicious']
        previous_attester_is_malicious = agent.context['previous_attester_is_malicious']
        previous_attestation_was_malicious = agent.context['previous_attestation_was_malicious']
        current_attester_fork_probability = agent.context['current_attester_fork_probability']

        #print("Current attester fork probability : ", agent.context['current_attester_fork_probability'])
        #print("Previous attestation was malicious : ", agent.context['previous_attestation_was_malicious'])

        action = None

        if (honest_head.hash != blockchain.head.hash):
            reverted_blocks, added_blocks = agent.context['blockchain'].find_path(agent.context['blockchain'].head, honest_head)
            agent.reorg(reverted_blocks, added_blocks)
        
        # if current_attester_is_malicious or previous_attester_is_malicious:
        #     # Deviate from the nominal behavior by attaching the block to the parent of the head
        #     malicous_head = blockchain.get_block(honest_head.parent_hash)
        #     reverted_blocks, added_blocks = agent.context['blockchain'].find_path(agent.context['blockchain'].head, malicous_head)
        #     agent.reorg(reverted_blocks, added_blocks)
        #     action = "MALICIOUS BLOCK PROPOSAL"

        state = torch.tensor([previous_attestation_was_malicious, current_attester_fork_probability], dtype=torch.float32).unsqueeze(0)
        action = agent.context['proposer_strategy'](state)
        _action = action.item()

        if _action == 1:
            # Deviate from the nominal behavior by attaching the block to the parent of the head
            malicous_head = blockchain.get_block(honest_head.parent_hash)
            reverted_blocks, added_blocks = agent.context['blockchain'].find_path(agent.context['blockchain'].head, malicous_head)
            agent.reorg(reverted_blocks, added_blocks)

        agent.context["factory"].push_proposer_history(state, action, agent.context["slot"])

        state_copy = agent.context['state'].copy()
        pending_transactions = agent.get_pending_transactions()
        selected_transactions = []

        #Select all pending transactions ordered by nonce
        for account in pending_transactions:
            pending_transactions[account].sort(key=lambda tx: tx.nonce)
            selected_transactions += pending_transactions[account]
        
        for selected_tx in selected_transactions:
            print(selected_tx)
            receipt = agent.context['vm'].process_tx(state_copy.copy(), selected_tx)
            state_copy.apply_batch_state_change(receipt.state_changes)
            pending_transactions[selected_tx.origin].remove(selected_tx)

            if len(pending_transactions[selected_tx.origin]) == 0:
                del pending_transactions[selected_tx.origin]
        
        block = agent.create_block(selected_transactions)

        # Loop though seeds until the block hash is greater than the forked block hash to ensure success of the attack
        while block.hash < honest_head.hash:
            block.seed = block.seed + 1
            block.hash = block.compute_hash()

        # call receive_block instead of append_block to trigger the beacon chain state update
        agent.receive_block(block)
        agent.propose_block(block)
        
    @staticmethod
    @export
    def create_block(agent: ExternalAgent, transactions: list[Transaction]) -> Block:
        """ Creates a block with the given transactions

            :param transactions: the transactions to include in the block
            :type transactions: list[Transaction]
            :returns: the block with the transactions included in it
            :rtype: Block
        """

        # Deviate from the nominal behavior by attaching the block to the parent of the head

        head = agent.context['blockchain'].head
        state = agent.context['beacon_states'][head.hash]
        slot = agent.context['slot']
        block = agent.context['factory'].build_block(head.hash, agent.name, slot, transactions)

        # Greedy attestation inclusion
        # for attestation in agent.context['attestations']:
            
        #     block.add_attestation(attestation)
        #     agent.context['attestations'].remove(attestation)

        for attestation in agent.context["latest_messages"].values():
            if state.is_attestation_included(attestation) is False:
                block.add_attestation(attestation)
        
        return block

    @staticmethod
    @export
    def propose_block(agent: ExternalAgent, block: Block):
        """ Propose a block to the network

            :param block: the block to propose to the network
            :type block: Block
        """
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseBlock(agent.name, block), outbound_peers)
