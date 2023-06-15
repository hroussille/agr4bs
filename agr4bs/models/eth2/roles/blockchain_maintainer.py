
"""
Ethereum 2.0 implementation of the BlockchainMaintainer role as per AGR4BS

BlockchainMaintainerContextChange:

The BlockchainMaintainerContextChange exposes changes that need to be made to the
ExternalAgent context when the Role is mounted and unmounted.
"""

from collections import defaultdict
import math

from ....events.events import INIT
from ....state.account import Account
from ....state.state_change import AddBalance, CreateAccount, RemoveBalance
from ....agents import ExternalAgent, Context, ContextChange, AgentType
from ....events import RECEIVE_BLOCK, RECEIVE_TRANSACTION, RECEIVE_BLOCK_ENDORSEMENT, NEXT_SLOT, NEXT_EPOCH
from ....state import State, Receipt
from ....network.messages import DiffuseBlock, DiffuseTransaction, RequestBlockEndorsement, DiffuseBlockEndorsement
from ....roles import Role, RoleType
from ....common import on, export
from ..blockchain import Block, Transaction, Attestation
from ..factory import Factory


class BlockchainMaintainerContextChange(ContextChange):

    """
        Context changes that need to be made to the ExternalAgent when
        the associated Role (BlockchainMaintainer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.receipts: dict[Receipt] = {}

        # tx_pool holds transactions ready to be processed
        self.tx_pool: dict[dict[Transaction]] = self.init_tx_pool

        self.vm = self.init_vm
        self.blockchain = self.init_blockchain
        self.state = self.init_state
        self.current_attesters = 0

        self.latest_messages = {}
        self.epoch = -1
        self.slot = 0

        # The current validators list
        self.validators = {}

        # The historical validator base rewards
        self.base_rewards = {}

        # The historical total effective balance
        self.total_effective_balance = {}

        # Wether or not we are an attester in the current slot
        self.attester = False

        # The attestations that we are currently taking into account
        self.attestations = []

        # The attesttions that we have not yet taken into account
        # Those will be unlocked at the next slot
        self.pending_attestations = []

        # The attestations that are included in what we consider as
        # the main chain divided by epoch
        self.included_attestations_per_epoch = defaultdict(lambda: [])

        # If the effective balance of a validator is below this value it will be kicked out
        self.minimum_effective_balance = 16 * 10 ** 18

        # Rewards configuration
        self.base_reward_factor = 64
        self.base_reward_per_epoch = 4
        self.timely_source_weight = 14
        self.timely_target_weight = 26
        self.timely_head_weight = 14
        self.sync_reward_weight = 2
        self.proposer_weight = 8


    @staticmethod
    def init_vm(context: Context):
        """
            Initialize the VM
        """
        factory: Factory = context['factory']

        return factory.build_vm()

    @staticmethod
    def init_blockchain(context: Context):
        """
            Initialize the blockchain
        """
        factory: Factory = context['factory']
        genesis: Block = context['genesis']

        return factory.build_blockchain(genesis)

    @staticmethod
    def init_state(context: Context):
        """
            Initialize the state
        """
        factory: Factory = context['factory']
        state: State = factory.build_state()

        return state

    @staticmethod
    def init_tx_pool(context: Context):
        """
            Initialize the tx pool
        """
        factory: Factory = context['factory']
        tx_pool = factory.build_tx_pool()

        return tx_pool


class BlockchainMaintainer(Role):

    """
        Implementation of the BlockchainMaintainer Role which must
        expose the following behaviors :
        - validate_transaction
        - validate_block
        - store_transaction
        - execute_transaction
        - append_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        dependencies = [RoleType.PEER]

        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER,
                         AgentType.EXTERNAL_AGENT, dependencies)

    @staticmethod
    def context_change() -> ContextChange:
        """RECEIVE_ATTESTATION
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockchainMaintainerContextChange()

    @staticmethod
    @export
    @on(INIT)
    def process_genesis(agent: ExternalAgent):
        """
            Initialize the blockchain by executing all the transactions
            in the genesis block.
        """

        genesis = agent.context['blockchain'].genesis

        for tx in genesis.transactions:
            agent.execute_transaction(tx)

    @staticmethod
    @export
    @on(RECEIVE_TRANSACTION)
    def receive_transaction(agent: ExternalAgent, tx: Transaction):
        """
            Behavior called on a RECEIVE_TRANSACTIOn event
            It is responsible for validating the transaction and storing it
            in the memory pool if it passes the checks.
        """

        tx_hash = tx.compute_hash()

        # Invalid tx hashes are not added nor propagated
        if tx.hash != tx_hash:
            return False

        # Skip invalid transactions
        if agent.validate_new_transaction(tx) is False:
            return False

        # Record transactions in the mempool
        agent.store_transaction(tx)

        # Diffuse the transaction to the outbound peers
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseTransaction(agent.name, tx), outbound_peers)

        return True

    @staticmethod
    @export
    @on(RECEIVE_BLOCK)
    def receive_block(agent: ExternalAgent, block: Block):
        """
            Behavior called on RECEIVE_BLOCK event.
            It is responsible for validating the block and appending and
            triggering it's addition to the blockchain.
        """

        block = block.from_serialized(block.serialize())
        block_hash = block.compute_hash()

        # Block is already known
        if agent.context['blockchain'].get_block(block_hash):
            return

        # Skip invalid blocks
        if agent.validate_block(block) is False:
            return

        agent.append_block(block)

        # Give the block reward to the block proposer
        agent.context['validators'][block.creator] += agent.context['base_rewards'][block.slot // 32][block.creator] * 8 / 60

        # The block is valid, we can clear our local list of attestations
        # As they are now included in the blockchain.
        for attestation in block.attestations:

            if attestation in agent.context['attestations']:
                agent.context['attestations'].remove(attestation)

            if attestation in agent.context['pending_attestations']:
                agent.context['pending_attestations'].remove(attestation)

        # Diffuse the block to the outbound peers
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseBlock(agent.name, block), outbound_peers)
        
        # Trigger the endorsement policy if required
        if agent.context['attester']:
            agent.send_system_message(RequestBlockEndorsement(agent.name), agent.name)

    @staticmethod
    @export
    @on(RECEIVE_BLOCK_ENDORSEMENT)
    def receive_attestation(agent: ExternalAgent, attestation: Attestation):
        """
            Behavior called on RECEIVE_ATTESTATION event.
            It is responsible for validating the attestation and appending and
            triggering it's addition to the local state.

            Attestations are only valid if they are included in a block
        """

        # Overwrite the latest attestation from the same agent
        # LMD GHOST rule for head selection
        if agent.context['slot'] - attestation.slot <= 32:
            agent.context['latest_messages'][attestation.agent_name] = attestation
            # Process the timely head weight vote
            agent.context['validators'][attestation.agent_name] += agent.context['base_rewards'][attestation.epoch][attestation.agent_name]  * 14 / 60
        else:
            return
        
        for key in list(agent.context['latest_messages'].keys()):
                if agent.context['latest_messages'][key].slot < agent.context['slot'] - 32:
                    del agent.context['latest_messages'][key]

        # This may be an issue if we receive an attestation AFTER it has been included in a block
        # by another agent (i.e. we receive the block before the attestation)
        # In this case we should validate if the attestation is known or not
        if attestation in agent.context['attestations'] or attestation in agent.context['pending_attestations']:
            return
        
        # The attestation is not pending, it is already included in the local chain
        if attestation in agent.context['included_attestations_per_epoch'][attestation.epoch]:
            return

        agent.context['pending_attestations'].append(attestation)

    @staticmethod
    @on(NEXT_SLOT)
    @export
    def merge_pending_attestations(agent: ExternalAgent, slot: int, attesters: list[str]):
        """
            Reset the attestation flag
        """
        assert slot == agent.context['slot'] + 1
        assert len(attesters) >= 1

        agent.context['attester'] = agent.name in attesters
        agent.context['attestations'] += agent.context['pending_attestations']
        agent.context['pending_attestations'] = []
        agent.context['slot'] = slot

    @staticmethod
    @on(NEXT_EPOCH)
    @export
    def next_epoch(agent: ExternalAgent, epoch: int, new_validators: list[str]):
        """
            Update the epoch and the validator balances for the next epoch
        """
        assert epoch == agent.context['epoch'] + 1
        agent.context['epoch'] = epoch
        
        agent.process_epoch_checkpoint_votes(epoch - 1)

        current_validators = list(agent.context['validators'].keys())

        # Kick out validators that have less than the minimum balance
        for validator in current_validators:
            if agent.context['validators'][validator] < agent.context['minimum_effective_balance']:
                del agent.context['validators'][validator]

        # Add the new validators to the validator set
        for new_validator in new_validators:
            agent.context['validators'][new_validator] = 32 * 10 ** 18
        
        # Update the historical total effective balance
        agent.context['total_effective_balance'][epoch] = sum(agent.context['validators'].values())

        # Compute the new epoch base rewards for all validators in the current epoch
        agent.context['base_rewards'][epoch] = {k: agent.compute_base_reward(k) for k in agent.context['validators']}

        
    @staticmethod
    @export
    def compute_votes_shares(agent: ExternalAgent, source: Block, target: Block, epoch: int):
        """
            Compute the voting power allocated to a specific link source -> target for a given epoch
        """

        included_attestations = agent.context['included_attestations_per_epoch'][epoch]

        def predicate(attestation: Attestation):
            validator = attestation.agent_name

            if (validator not in agent.context['validators']):
                return False
            
            if (agent.context['validators'][validator] < agent.context['minimum_effective_balance']):
                return False

            return attestation.source == source.hash and attestation.target == target.hash

        filtered_attestations = list(filter(predicate, included_attestations))

        # Compute the total shares for the given source -> target link
        shares = sum([agent.context['validators'][attestation.agent_name] for attestation in filtered_attestations])

        # Return the shares divided by the total effective balance for the given epoch
        return shares / agent.context['total_effective_balance'][epoch]

    @staticmethod
    @export
    def process_epoch_checkpoint_votes(agent: ExternalAgent, epoch: int):
        """
            Process the votes for the epoch checkpoint and justify / finalize blocks
            as necessary
        """
        if epoch <= 0:
            return

        #source = agent.context['blockchain'].get_last_justified_block()
        source = agent.context['blockchain'].last_justified_block
        target = agent.context['blockchain'].get_checkpoint_from_epoch(epoch)

        if epoch >= 1:

            # If source -> target is voted by 2/3 of the validators balance then we justify it
            if agent.compute_votes_shares(source, target, epoch) >= 2/3:

                #print(f"Agent {agent.name} justified block {target.hash} at epoch {epoch}")
                agent.context['blockchain'].justify_block(target)

                # If source was justified, it must be finalized
                if source.justified is True:
                    #print(f"Agent {agent.name} finalized block {source.hash} at epoch {epoch}")
                    agent.context['blockchain'].finalize_block(source)

        if epoch >= 2:
            b = agent.context['blockchain'].get_checkpoint_from_epoch(epoch - 2)
            c = target
            d = source

            if b.justified:
                if agent.compute_votes_shares(b, c, epoch - 1) >= 2/3:
                    agent.context['blockchain'].finalize_block(b)
                
                if c.justified and agent.compute_votes_shares(b, d, epoch) >= 2/3:
                    agent.context['blockchain'].finalize_block(b)

        if epoch >= 3:
            a = agent.context['blockchain'].get_checkpoint_from_epoch(epoch - 3)
            b = agent.context['blockchain'].get_checkpoint_from_epoch(epoch - 2)
            c = target
            d = source

            if a.justified and b.justified and agent.compute_votes_shares(a, c, epoch - 1) >= 2/3:
                agent.context['blockchain'].finalize_block(a)

        epoch_attestations = agent.context['included_attestations_per_epoch'][epoch]
        validator_attestations = {k: [] for k in agent.context['validators']}

        for attestation in epoch_attestations:
            validator_attestations[attestation.agent_name].append(attestation)

        for validator in agent.context['validators']:

            # If we don't pass this assertion then we have a bug in the code
            # As a dupplicated attestation should be refused by the network
            assert len(validator_attestations[validator]) <= 1

            reward = 0

            # Penalty for not attesting in the current epoch
            if len(validator_attestations[validator]) == 0:
                reward = -30
                # TODO: Delay this computation by one slot to avoid missing attestations ?
                continue
            
            # Reward for attesting  with a correct source
            if validator_attestations[validator][0].source == source.hash:
                reward = reward + 14

            # Reward for attesting with a correct target
            if validator_attestations[validator][0].target == target.hash:
                reward = reward + 26
            
            agent.context['validators'][validator] += agent.context['base_rewards'][epoch][validator] * reward / 60



        
    @staticmethod
    @export
    def validate_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Validate a transaction to execute

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """

        sender_account = agent.context['state'].get_account(tx.origin)

        if tx.hash in agent.context['receipts']:
            return False

        if sender_account is None:
            return False

        if sender_account.balance < tx.value + tx.fee:
            return False

        if sender_account.nonce != tx.nonce:
            return False

        return True

    @staticmethod
    @export
    def validate_new_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Validate a newly received transaction specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """

        if tx.hash in agent.context['receipts']:
            return False

        sender_account = agent.context['state'].get_account(tx.origin)

        if sender_account is None:
            return False

        if sender_account.nonce > tx.nonce:
            return False

        # This special case may save a network diffuse on invalid tx with correct nonce
        if sender_account.nonce == tx.nonce:
            if sender_account.balance < tx.value + tx.fee:
                return False

        # Replacement is only allowed if the replacement fee is higher than the existing one
        if tx.origin in agent.context['tx_pool'] and tx.nonce in agent.context['tx_pool'][tx.origin]:
            exising_tx = agent.context['tx_pool'][tx.origin][tx.nonce]
            if (tx.fee <= exising_tx.fee):
                return False

        return True

    @staticmethod
    @export
    def validate_block(agent: ExternalAgent, block: Block) -> bool:
        """ Validate a specific Block

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """

        if block.compute_hash() != block.hash:
            return False

        return True

    @staticmethod
    @export
    def get_pending_transactions(agent: ExternalAgent) -> dict[list[Transaction]]:
        pending_transactions_by_account = {}

        for account in agent.context['tx_pool']:
            account_nonce = agent.context['state'].get_account_nonce(account)

            if account_nonce in agent.context['tx_pool'][account]:
                nonce = account_nonce
                pending_transactions_by_account[account] = []

                while nonce in agent.context['tx_pool'][account]:
                    pending_transactions_by_account[account].append(
                        agent.context['tx_pool'][account][nonce])
                    nonce = nonce + 1

        return pending_transactions_by_account

    @staticmethod
    @export
    def store_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Store a specific transaction from the transaction pool

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """

        # The sender is not known create entires in the tx_pool
        if tx.origin not in agent.context['tx_pool']:
            agent.context['tx_pool'][tx.origin] = {}

        agent.context['tx_pool'][tx.origin][tx.nonce] = tx

    @staticmethod
    @export
    def discard_transaction(agent: ExternalAgent, tx: Transaction):
        """
            discard a specific transaction from the transaction pool

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to discard
            :type transaction: Transaction
        """

        # The transaction may be unknown if it was received in a foreign block
        if tx.origin in agent.context['tx_pool'] and tx.nonce in agent.context['tx_pool'][tx.origin]:
            del agent.context['tx_pool'][tx.origin][tx.nonce]

            # Cleanup the tx_pool when an account has no pending or queued transactions
            if len(agent.context['tx_pool'][tx.origin]) == 0:
                del agent.context['tx_pool'][tx.origin]

    @staticmethod
    @export
    def append_block(agent: ExternalAgent, block: Block) -> bool:
        """ Append a specific block to the local blockchain

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        if agent.validate_block(block):
            head_changed, reverted_blocks, added_blocks = agent.context['blockchain'].add_block(
                block)

            # Only reorg if the head did not change :
            # If the head changed then we added on the main chain
            # If the head did not change then we added on a side chain that may become the main chain
            if head_changed is False:

                latest_messages = list(agent.context['latest_messages'].values())

                # Processing the latest messages up to that point may yield a new head
                # If this is a case we need to reorg the chain right now
                reverted_blocks, added_blocks = agent.context['blockchain'].process_block_votes(latest_messages)

            else:
                for attestation in block.attestations:
                    if attestation in agent.context['attestations']:
                        agent.context['attestations'].remove(attestation)
                    
                    # Register the attestation as part of the local main chain
                    agent.context['included_attestations_per_epoch'][attestation.epoch].append(attestation)

                    # Add the inclusion delay rewards
                    delay = abs(block.slot - attestation.epoch)
                    base_reward = agent.context['base_rewards'][block.slot // 32][attestation.agent_name]

                    agent.context['validators'][attestation.agent_name] += base_reward * (1 / delay)

            # Execute the transactions
            agent.reorg(reverted_blocks, added_blocks)

            return True

        return False

    @staticmethod
    @export
    def reorg(agent: ExternalAgent, reverted_blocks: list[Block], added_blocks: list[Block]):
        """
            Process a chain reorg by doing the adequate revert / execute
        """

        for reverted_block in reverted_blocks:
            agent.reverse_block(reverted_block)

        for added_block in added_blocks:

            # An invalid block was found during the reorg :
            # - invalidate the block and all its successors
            # - compute new candidate head
            # - reorg to the new head
            if not agent.execute_block(added_block):
                if agent.context["blockchain"].mark_invalid(added_block):
                    previous_head = agent.context["blockchain"].get_block(
                        added_block.parent_hash)
                    new_head = agent.context["blockchain"].find_new_head()

                    if previous_head.hash != new_head.hash:
                        to_revert, to_add = agent.context["blockchain"].find_path(
                            previous_head, new_head)
                        agent.reorg(to_revert, to_add)

                    else:
                        agent.context["blockchain"].head = previous_head

                    return

    @staticmethod
    @export
    def execute_block(agent: ExternalAgent, block: Block) -> bool:
        """ Execute a specific Block

            :param block: the Block to execute
            :type block: Block
            :returns: wether the Block was executed successfully or not
            :rtype: bool
        """

        for index, tx in enumerate(block.transactions):

            if agent.validate_transaction(tx) is False:

                # An invalid tx was found while executing the block
                # Revert all the previous ones from the same block
                while index > 0:
                    agent.reverse_transaction(block.transactions[index - 1])
                    agent.store_transaction(block.transactions[index - 1])
                    index = index - 1

                return False

            agent.execute_transaction(tx)
            agent.discard_transaction(tx)

        if agent.context['state'].get_account(block.creator) is None:
            change = CreateAccount(Account(block.creator, 0))
            agent.context["state"].apply_state_change(change)
        
        agent.context["blockchain"].head = block

        return True

    @staticmethod
    @export
    def reverse_block(agent: ExternalAgent, block: Block) -> bool:
        """ Reverse a specific Block

            :param block: the Block to reverse
            :type block: Block
            :returns: wether the Block was reversed successfully or not
            :rtype: bool
        """
        for tx in reversed(block.transactions):

            # Reverse the transaction
            agent.reverse_transaction(tx)

            # Delete the Receipt entry
            del agent.context['receipts'][tx.hash]

        for attestation in block.attestations:
            agent.context['included_attestations_per_epoch'][attestation.epoch].remove(attestation)

        new_head = agent.context['blockchain'].get_block(block.parent_hash)
        agent.context["blockchain"].head = new_head

    @staticmethod
    @export
    def execute_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        if tx.hash in agent.context['receipts']:
            raise ValueError("Executing an already seen transaction.")

        receipt = agent.context['vm'].process_tx(
            agent.context["state"].copy(), tx)

        agent.context["state"].apply_batch_state_change(receipt.state_changes)
        agent.context["receipts"][tx.hash] = receipt

    @staticmethod
    @export
    def reverse_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Reverse a specific transaction

            :param transaction: the transaction to reverse
            :type transaction: Transaction
            :returns: wether the transaction was reverted successfully or not
            :rtype: bool
        """
        if tx.hash not in agent.context['receipts']:
            raise ValueError("Reversing an uknown transaction")

        receipt: Receipt = agent.context['receipts'][tx.hash]

        changes = [sc.revert() for sc in reversed(receipt.state_changes)]
        agent.context['state'].apply_batch_state_change(changes)

        return True
    
    @staticmethod
    @export
    def compute_base_reward(agent: ExternalAgent, validator: str) -> int:
        """
            Compute the base reward for a given validator

            :param validator: the validator to compute the base reward for
            :type validator: str
            :returns: the base reward for the given validator at the current epoch
            :rtype: int
        """
        base_reward_factor = agent.context['base_reward_factor']
        base_reward_per_epoch = agent.context['base_reward_per_epoch']
        effective_balance = agent.context['validators'][validator]
        total_effective_balance = agent.context['total_effective_balance'][agent.context['epoch']]

        return int(effective_balance * (base_reward_factor / (base_reward_per_epoch * math.sqrt(total_effective_balance))))

