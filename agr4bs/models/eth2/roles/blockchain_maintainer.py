
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
from ..blockchain import Block, Transaction, Attestation, Blockchain
from ..factory import Factory
from ..consensus import BeaconState
from ..constants import SLOTS_PER_EPOCH, INACTIVITY_SCORE_BIAS, INACTIVITY_SCORE_RECOVERY_RATE, INACTIVITY_PENALTY_QUOTIENT_BELLATRIX, EFFECTIVE_BALANCE_INCREMENT, PARTICIPATION_FLAG_WEIGHTS, WEIGHT_DENOMINATOR, PROPOSER_WEIGHT, TIMELY_TARGET_FLAG_INDEX, TIMELY_HEAD_FLAG_INDEX, TIMELY_SOURCE_FLAG_INDEX, JUSTIFICATION_BITS_LENGTH, MIN_ATTESTATION_INCLUSION_DELAY


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

        # Beacon state dict indexed by block hash
        self.beacon_states = {} # type: dict[str, BeaconState]

        # Wether or not we are an attester in the current slot
        self.attester = False

        # The attestations that we are currently taking into account
        self.attestations = []

        # The attesttions that we have not yet taken into account
        # Those will be unlocked at the next slot
        self.pending_attestations = []

        # The attestations that are included in the chain (main chain or fork)
        self.included_attestations_per_epoch = defaultdict(lambda: [])


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
    def init_beacon_state(context: Context):
        """
            Initialize the beacon state
        """
        genesis: Block = context['genesis']

        return BeaconState(genesis)

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
        agent.context['beacon_states'][genesis.hash] = BeaconState(genesis)
        agent.execute_block(genesis)

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

        # Block is already known￼
        if agent.context['blockchain'].get_block(block_hash) is not None:
            return

        # Block is invalid
        if agent.validate_block(block) is False:
            return

        # Create a new beacon state from the parent state
        state: BeaconState = agent.context['beacon_states'][block.parent_hash].copy()
        state.update_latest_block(block)
        state = agent.process_slots(state, block.slot)
        
        # Append the block to the blockchain
        agent.append_block(block)

        # Process the block attestations
        agent.process_attestations(block, state)

        # Diffuse the block to the outbound peers
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseBlock(agent.name, block), outbound_peers)
        
        # Store the new beacon state
        agent.context['beacon_states'][block_hash] = state

        # Trigger the endorsement policy if required
        if agent.context['attester']:
            ##print("Triggering endorsement policy for", agent.name, "on block", block_hash, "slot", block.slot)
            agent.send_system_message(RequestBlockEndorsement(agent.name), agent.name)

    @staticmethod
    @export
    def process_attestations(agent: ExternalAgent, block: Block, state: BeaconState):
        """
            Process the attestations included in the given block
        """           
        for attestation in block.attestations:
            agent.process_attestation(attestation, state)

            if attestation in agent.context['attestations']:
                agent.context['attestations'].remove(attestation)

    @staticmethod
    @export
    def process_attestation(agent: ExternalAgent, attestation: Attestation, state: BeaconState):
        """
            Process the attestations included in the given block
        """

        target = agent.context['blockchain'].get_block(attestation.target)
        target_epoch = target.slot // SLOTS_PER_EPOCH

        assert target is not None
        assert target_epoch in (state.previous_epoch(), state.current_epoch())
        assert attestation.slot + MIN_ATTESTATION_INCLUSION_DELAY <= state.slot <= attestation.slot + SLOTS_PER_EPOCH
              
        # Participation flag indices
        participation_flag_indices = agent.get_attestation_participation_flag_indices(state, attestation, state.slot - attestation.slot)

        # Update epoch participation flags
        if target_epoch == state.current_epoch():
            epoch_participation = state.current_epoch_participation
        else:
            epoch_participation = state.previous_epoch_participation

        proposer_reward_numerator = 0

        def has_flag(participation, flag):
            bit_flag = 2 ** flag
            return participation & bit_flag == bit_flag
        
        def add_flag(participation, flag):
            bit_flag = 2 ** flag
            return participation | bit_flag

        for flag_index, weight in enumerate(PARTICIPATION_FLAG_WEIGHTS):

            if attestation.agent_name not in epoch_participation:
                epoch_participation[attestation.agent_name] = 0

            if flag_index in participation_flag_indices and not has_flag(epoch_participation[attestation.agent_name], flag_index):
                epoch_participation[attestation.agent_name] = add_flag(epoch_participation[attestation.agent_name], flag_index)
                proposer_reward_numerator += state.get_base_reward(attestation.agent_name) * weight

        # Reward proposer
        proposer_reward_denominator = (WEIGHT_DENOMINATOR - PROPOSER_WEIGHT) * WEIGHT_DENOMINATOR // PROPOSER_WEIGHT

        # TODO: Check if this is correct ( Gwei )
        proposer_reward = proposer_reward_numerator // proposer_reward_denominator

        state.reward_validator(state.latest_block().creator, proposer_reward)

    @staticmethod
    @export
    def get_attestation_participation_flag_indices(agent: ExternalAgent, state: BeaconState, attestation: Attestation, inclusion_delay: int) -> list[int]:
        """
        Return the flag indices that are satisfied by an attestation.
        """

        target = agent.context['blockchain'].get_block(attestation.target)
        target_epoch = target.slot // SLOTS_PER_EPOCH

        if target_epoch == state.current_epoch():
            justified_checkpoint = state.current_justified_checkpoint()
        else:
            justified_checkpoint = state.previous_justified_checkpoint()


        expected_target = agent.context['blockchain'].get_checkpoint_from_epoch(target_epoch, state.latest_block())
        expected_head = agent.context['blockchain'].get_block_for_slot(attestation.slot, state.latest_block())

        # Matching roots
        is_matching_source = attestation.source == justified_checkpoint.hash
        is_matching_target = is_matching_source and attestation.target == expected_target.hash
        is_matching_head = is_matching_target and attestation.root == expected_head.hash

        assert is_matching_source

        participation_flag_indices = []
        if is_matching_source and inclusion_delay <= int(math.sqrt((SLOTS_PER_EPOCH))):
            participation_flag_indices.append(TIMELY_SOURCE_FLAG_INDEX)
        if is_matching_target and inclusion_delay <= SLOTS_PER_EPOCH:
            participation_flag_indices.append(TIMELY_TARGET_FLAG_INDEX)
        if is_matching_head and inclusion_delay == MIN_ATTESTATION_INCLUSION_DELAY:
            participation_flag_indices.append(TIMELY_HEAD_FLAG_INDEX)

        return participation_flag_indices

    @staticmethod
    @export
    def get_inactivity_penalty_deltas(agent: ExternalAgent, state: BeaconState) -> tuple[list[int], list[int]]:
        """
        Return the inactivity penalty deltas by considering timely target participation flags and inactivity scores.
        """
        rewards = { validator: 0 for validator in state.validators }
        penalties = { validator: 0 for validator in state.validators }
        previous_epoch = state.previous_epoch()
        matching_target_indices = state.get_participation(previous_epoch, TIMELY_TARGET_FLAG_INDEX)
        for validator in state.get_eligible_validators():
            if validator not in matching_target_indices:
                penalty_numerator = state.effective_balances[validator] * state.inactivity_scores[validator]
                penalty_denominator = INACTIVITY_SCORE_BIAS * INACTIVITY_PENALTY_QUOTIENT_BELLATRIX
                penalties[validator] += penalty_numerator // penalty_denominator

        return rewards, penalties

    @staticmethod
    @export
    def process_rewards_and_penalties(agent: ExternalAgent, state: BeaconState) -> None:
        """
        Processes the rewards and penalties at the end of the epoch.
        """
        
        # No rewards are applied at the end of `GENESIS_EPOCH` because rewards are for work done in the previous epoch
        if state.current_epoch() == 0:
            return

        flag_deltas = [agent.get_flag_index_deltas(state, flag_index) for flag_index in range(len(PARTICIPATION_FLAG_WEIGHTS))]

        deltas = flag_deltas + [agent.get_inactivity_penalty_deltas(state)]

        for (rewards, penalties) in deltas:
            for validator in state.validators:
                state.reward_validator(validator, rewards[validator])
                state.penalize_validator(validator, penalties[validator])

    @staticmethod
    @export
    def get_flag_index_deltas(agent: ExternalAgent, state: BeaconState, flag_index: int) -> tuple[list[int], list[int]]:
        """
        Return the deltas for a given ``flag_index`` by scanning through the participation flags.
        """
        previous_epoch = state.previous_epoch()
        rewards = { validator: 0 for validator in state.validators }
        penalties = { validator: 0 for validator in state.validators }

        unslashed_validators = state.get_participation(previous_epoch, flag_index)

        weight = PARTICIPATION_FLAG_WEIGHTS[flag_index]

        unslashed_participating_balance = state.get_group_effective_balance(unslashed_validators)
        unslashed_participating_increments = unslashed_participating_balance // EFFECTIVE_BALANCE_INCREMENT
        active_increments = state.get_total_effective_balance() // EFFECTIVE_BALANCE_INCREMENT

        for validator in state.get_eligible_validators():
            base_reward = state.get_base_reward(validator)
            if validator in unslashed_validators:
                if not state.is_in_inactivity_leak():
                    reward_numerator = base_reward * weight * unslashed_participating_increments
                    rewards[validator] += reward_numerator // (active_increments * WEIGHT_DENOMINATOR)

            elif flag_index != TIMELY_HEAD_FLAG_INDEX:
                penalties[validator] += base_reward * weight // WEIGHT_DENOMINATOR

        return rewards, penalties

    @staticmethod
    @export
    def process_slots(agent: ExternalAgent, state: BeaconState, slot: int):
        """
            Fast forwards a parent state to the given slot and processes the epoch on the start slot of the next epoch
        """
        assert state.slot < slot

        while state.slot < slot:
            # Process epoch on the start slot of the next epoch
            if (state.slot + 1) % SLOTS_PER_EPOCH == 0:
                agent.process_epoch(state)

            state.slot = state.slot + 1

        return state
    
    @staticmethod
    @export
    def process_epoch(agent: ExternalAgent, state: BeaconState):
        """
            Process the epoch given the current state
        """
        agent.process_justification_and_finalization(state)
        agent.process_inactivity_updates(state)  # [New in Altair]
        agent.process_rewards_and_penalties(state)
        # agent.process_registry_updates(state)
        # agent.process_slashings(state)  # [Modified in Altair]
        state.process_effective_balance_updates()
        state.process_participation_flag_updates()

    @staticmethod
    @export
    def process_justification_and_finalization(agent: ExternalAgent, state: BeaconState):
        """
            Process the justification and finalization of the given state
        """
        
        # Skip the first epoch as it cannot be justified
        if state.current_epoch() <= 1:
            return
        
        previous_participants = state.get_participation(state.previous_epoch(), TIMELY_TARGET_FLAG_INDEX)
        current_participants = state.get_participation(state.current_epoch(), TIMELY_TARGET_FLAG_INDEX)
        total_active_balance = state.get_total_effective_balance()

        previous_target_balance = state.get_group_effective_balance(previous_participants)
        current_target_balance = state.get_group_effective_balance(current_participants)

        agent.weight_justification_and_finalization(state, total_active_balance, previous_target_balance, current_target_balance)

    @staticmethod
    @export
    def weight_justification_and_finalization(agent: ExternalAgent, state: BeaconState, total_active_balance: int, previous_epoch_target_balance: int, current_epoch_target_balance: int):
        """
            Weight the justification and finalization of the given state.
        """
        previous_epoch = state.previous_epoch()
        current_epoch = state.current_epoch()

        old_previous_justified_checkpoint = agent.context['blockchain'].get_block(state.previous_justified_checkpoint().hash)
        old_current_justified_checkpoint = agent.context['blockchain'].get_block(state.current_justified_checkpoint().hash)

        #old_previous_justified_checkpoint = state.previous_justified_checkpoint()
        #old_current_justified_checkpoint = state.current_justified_checkpoint()

        # Process justifications
        state.update_previous_justified_checkpoint(state.current_justified_checkpoint())
        state.justification_bits[1:] = state.justification_bits[:JUSTIFICATION_BITS_LENGTH - 1]
        state.justification_bits[0] = 0b0

        if previous_epoch_target_balance * 3 >= total_active_balance * 2:
            #print("JUSTIFYING PREVIOUS EPOCH")
            checkpoint = agent.context['blockchain'].get_checkpoint_from_epoch(previous_epoch, state.latest_block())
            agent.context['blockchain'].justify_block(checkpoint)
            state.update_current_justified_checkpoint(checkpoint)
            state.justification_bits[1] = 0b1

        if current_epoch_target_balance * 3 >= total_active_balance * 2:
            #print("JUSTIFYING CURRENT EPOCH")
            checkpoint = agent.context['blockchain'].get_checkpoint_from_epoch(current_epoch, state.latest_block())
            agent.context['blockchain'].justify_block(checkpoint)
            state.update_current_justified_checkpoint(checkpoint)
            state.justification_bits[0] = 0b1

        # Process finalizations
        bits = state.justification_bits
        old_previous_justified_checkpoint_epoch = old_previous_justified_checkpoint.slot // SLOTS_PER_EPOCH
        old_current_justified_checkpoint_epoch = old_current_justified_checkpoint.slot // SLOTS_PER_EPOCH

        def cleanup_state(hash: str):

            current_state = agent.context['beacon_states'][hash]

            while current_state:
                current_block = current_state.latest_block()
                parent_block = agent.context['blockchain'].get_block(current_block.parent_hash)

                if not parent_block:
                    break

                if parent_block.hash not in agent.context['beacon_states']:
                    break

                current_state = agent.context['beacon_states'][parent_block.hash]

                del agent.context['beacon_states'][parent_block.hash]
        
        # The 2nd/3rd/4th most recent epochs are justified, the 2nd using the 4th as source
        if all(bits[1:4]) and old_previous_justified_checkpoint_epoch + 3 == current_epoch:
            state.update_finalized_checkpoint(old_previous_justified_checkpoint)
        
        # The 2nd/3rd most recent epochs are justified, the 2nd using the 3rd as source
        if all(bits[1:3]) and old_previous_justified_checkpoint_epoch + 2 == current_epoch:
            state.update_finalized_checkpoint(old_previous_justified_checkpoint)

        # The 1st/2nd/3rd most recent epochs are justified, the 1st using the 3rd as source
        if all(bits[0:3]) and old_current_justified_checkpoint_epoch + 2 == current_epoch:
            state.update_finalized_checkpoint(old_current_justified_checkpoint)

        # The 1st/2nd most recent epochs are justified, the 1st using the 2nd as source
        if all(bits[0:2]) and old_current_justified_checkpoint_epoch + 1 == current_epoch:
            state.update_finalized_checkpoint(old_current_justified_checkpoint)

        cleanup_state(state.finalized_checkpoint().hash)
        agent.context['blockchain'].finalize_block(state.finalized_checkpoint())
    
    @staticmethod
    @export
    def process_inactivity_updates(agent: ExternalAgent, state: BeaconState) -> None:
        """
            Update the validators innactivity scores based on their participation in the previous epoch
        """

        # Skip the genesis epoch as score updates are based on the previous epoch participation
        if state.current_epoch() == 0:
            return

        timely_target_flags = state.get_participation(state.previous_epoch(), TIMELY_TARGET_FLAG_INDEX)

        for validator in state.get_eligible_validators():

            # Increase the inactivity score of inactive validators
            if validator in timely_target_flags:
                state.inactivity_scores[validator] -= min(1, state.inactivity_scores[validator])
            else:
                state.inactivity_scores[validator] += INACTIVITY_SCORE_BIAS
            # Decrease the inactivity score of all eligible validators during a leak-free epoch
            if not state.is_in_inactivity_leak():
                state.inactivity_scores[validator] -= min(INACTIVITY_SCORE_RECOVERY_RATE, state.inactivity_scores[validator])
                
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

        # This may be an issue if we receive an attestation AFTER it has been included in a block
        # by another agent (i.e. we receive the block before the attestation)
        # In this case we should validate if the attestation is known or not
        if attestation in agent.context['attestations'] or attestation in agent.context['pending_attestations']:
            #print("Attestation is already known")
            return
        
        # Use the gossip validation rules
        if not agent.validate_attestation(attestation, gossip=True):
            #print("Attestation is not valid")
            return
    
        # Overwrite the latest attestation from the same agent
        # LMD GHOST rule for head selection 
        agent.context['latest_messages'][attestation.agent_name] = attestation
        
        # Clear the latest messages that are too old
        for key in list(agent.context['latest_messages'].keys()):
                if agent.context['latest_messages'][key].slot < agent.context['slot'] - SLOTS_PER_EPOCH:
                    del agent.context['latest_messages'][key]
        
        # The attestation is not pending, it is already included in the local chain
        if attestation in agent.context['included_attestations_per_epoch'][attestation.epoch]:
            #print("Attestation is already included in the local chain")
            return

        agent.context['pending_attestations'].append(attestation)

    @staticmethod
    @export
    def validate_attestation(agent: ExternalAgent, attestation: Attestation, gossip: bool = False):
        """
            Validate an attestation
        """

        # The attestation is in a future slot.
        # In gossip we allow attestations from the current slot
        if attestation.slot > agent.context['slot'] or not gossip and attestation.slot == agent.context['slot']:
            #print("Attestation is in the future")
            return False

        ##print("Attestation is in the past")

        # The attestation is older than the maximum allowed
        if attestation.slot < agent.context['slot'] - SLOTS_PER_EPOCH:
            #print("Attestation from", attestation.agent_name , "is too old", attestation.slot, agent.context['slot'])
            #print(attestation)
            return False
        
        ##print("Attestation is not too old")

        blockchain: Blockchain = agent.context['blockchain']
        root = blockchain.get_block(attestation.root)
        target_block = blockchain.get_block(attestation.target)
        source_block = blockchain.get_block(attestation.source)

        # In gossip, we may not have the blocks in our blockchain
        if root is None and gossip is False:
            #print("Attestation is refering to an unknown root")
            return False
        
        # In gossip, we may not have the target block in our blockchain yet
        # This can happen in the begining of epochs
        if target_block is None and gossip is False:
            #print("Attestation is refering to an unknown target")
            return False
        
        if source_block is None:
            #print("Attestation is refering to an unknown source")
            return False

        # The attestation is for a block that is not extending the finalized chain
        if source_block.hash != blockchain.genesis.hash:
            if not blockchain.is_close_parent(source_block, blockchain.last_finalized_block, abs(source_block.slot - blockchain.last_finalized_block.slot)):
                #print("Last finalized : ", blockchain.last_finalized_block.hash, "height ", blockchain.last_finalized_block.height)
                #print("Source : ", source_block.hash, "height ", source_block.height)
                #print("Attestation is not extending the finalized chain")
                return False

        ##print("Attestation is extending the finalized chain")

        current_checkpoint = blockchain.get_checkpoint_from_epoch(agent.context['epoch'], root)
        previous_checkpoint = blockchain.get_checkpoint_from_epoch(max(agent.context['epoch'] - 1, 0), root)

        # The attestation should be for the current or previous checkpoint according to the chain that is being built
        if not gossip and attestation.target != current_checkpoint.hash and attestation.target != previous_checkpoint.hash:
            #print("Invalid target !")
            # #print(gossip)
            # #print(attestation.slot)
            # #print(agent.context['slot'])
            # #print("Attestation is not for the current or previous checkpoint")
            # #print("Current checkpoint : ", current_checkpoint.hash)
            # #print("Previous checkpoint : ", previous_checkpoint.hash)
            # #print("Attestation target : ", attestation.target)
            return False

        ##print("Attestation is for the current or previous checkpoint")

        return True
    
    @staticmethod
    @on(NEXT_SLOT)
    @export
    def next_slot(agent: ExternalAgent, slot: int, attesters: list[str]):
        """
            Reset the attestation flag
        """
        assert slot == agent.context['slot'] + 1
        assert len(attesters) >= 1

        # Register if the agent is an attester for the current slot
        agent.context['attester'] = agent.name in attesters

        # Merge the pending attestations
        agent.context['attestations'] += agent.context['pending_attestations']
        agent.context['pending_attestations'] = []

        # Update the slot
        agent.context['slot'] = slot

    @staticmethod
    @on(NEXT_EPOCH)
    @export
    def next_epoch(agent: ExternalAgent, epoch: int):
        """
            Update the epoch and the validator balances for the next epoch
        """
        assert epoch == agent.context['epoch'] + 1
        agent.context['epoch'] = epoch
        
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
        
        for attestation in block.attestations:
            if not agent.validate_attestation(attestation):
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
                # If this is the case we need to reorg the chain right now
                reverted_blocks, added_blocks = agent.context['blockchain'].process_block_votes(latest_messages)

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

            # Process the deposit transactions to update the beacon state
            if tx.to == "deposit_contract" and agent.context['receipts'][tx.hash].reverted is False:
                agent.context['beacon_states'][block.hash].add_validator(tx.origin)

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
    

