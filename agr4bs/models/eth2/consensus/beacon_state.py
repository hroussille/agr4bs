import math

from BitVector import *

from ..constants import NEW_VALIDATOR_BALANCE, SLOTS_PER_EPOCH, MIN_EPOCHS_TO_INACTIVITY_PENALTY , JUSTIFICATION_BITS_LENGTH, DOWNWARD_THRESHOLD, UPWARD_THRESHOLD, EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE, BASE_REWARD_FACTOR
from ..blockchain import Block
from ....common import Serializable

class BeaconState (Serializable):
    """
        The state of the beacon chain
    """

    def __init__(self, genesis: Block) -> None:
        self._epoch = 0
        self._slot = 0
        self._validators = []

        # balances are stored in wei
        self._balances = {}

        # effective balances are stored in wei
        self._effective_balances = {}

        # inactivity scores
        self._inactivity_scores = {}

        assert genesis.justified and genesis.finalized

        # Checkpoints informations
        self._current_justified_checkpoint = genesis
        self._previous_justified_checkpoint = genesis
        self._finalized_checkpoint = genesis

        self._latest_block = genesis

        self._current_participations = {}
        self._previous_participations = {}
        self._justification_bits = BitVector(size=JUSTIFICATION_BITS_LENGTH)

    @property
    def slot(self) -> int:
        """
            Get the slot of the state
        """
        return self._slot
    
    @slot.setter
    def slot(self, value: int) -> None:
        """epoch
            Set the slot of the state
        """
        self._slot = value
        self._epoch = self._slot // SLOTS_PER_EPOCH
    
    def add_validator(self, validator: str) -> None:
        """
            Add a new validator to the state
        """
        assert validator not in self._validators

        self._validators.append(validator)
        self._balances[validator] = NEW_VALIDATOR_BALANCE
        self._effective_balances[validator] = NEW_VALIDATOR_BALANCE
        self._inactivity_scores[validator] = 0

    def current_epoch(self) -> int:
        """
            Returns the current epoch
        """
        return self._epoch
    
    def previous_epoch(self) -> int:
        """
            Returns the previous epoch
        """
        return self._epoch - 1
    
    def current_slot(self) -> int:
        """
            Returns the current slot
        """
        return self._slot
    
    def previous_slot(self) -> int:
        """
            Returns the previous slot
        """
        return self._slot - 1
    
    def latest_block(self) -> Block:
        """
            Returns the latest block
        """
        return self._latest_block
    
    def current_justified_checkpoint(self) -> Block:
        """
            Returns the current justified checkpoint
        """
        return self._current_justified_checkpoint
    
    def previous_justified_checkpoint(self) -> Block:
        """
            Returns the previous justified checkpoint
        """
        return self._previous_justified_checkpoint
    
    def finalized_checkpoint(self) -> Block:
        """
            Returns the finalized checkpoint
        """
        return self._finalized_checkpoint
    
    def update_current_justified_checkpoint(self, checkpoint: Block) -> None:
        """
            Update the current justified checkpoint
        """
        assert checkpoint.slot >= self._current_justified_checkpoint.slot

        self._current_justified_checkpoint = checkpoint

    def update_previous_justified_checkpoint(self, checkpoint: Block) -> None:
        """
            Update the previous justified checkpoint
        """
        assert checkpoint.slot >= self._previous_justified_checkpoint.slot

        self._previous_justified_checkpoint = checkpoint

    def update_finalized_checkpoint(self, checkpoint: Block) -> None:
        """
            Update the finalized checkpoint
        """
        assert checkpoint.slot >= self._finalized_checkpoint.slot

        self._finalized_checkpoint = checkpoint

    def update_latest_block(self, block: Block) -> None:
        """
            Update the latest block
        """
        assert block.slot >= self._latest_block.slot

        self._latest_block = block

    @property
    def validators(self) -> list[str]:
        """
            Get the validators of the state
        """
        return self._validators
    
    @property
    def balances(self) -> dict[str, int]:
        """
            Get the balances of the state
        """
        return self._balances
    
    @property
    def effective_balances(self) -> dict[str, int]:
        """
            Get the effective balances of the state
        """
        return self._effective_balances
    
    @property
    def inactivity_scores(self) -> dict[str, int]:
        """
            Get the inactivity scores of the state
        """
        return self._inactivity_scores
    
    def reward_validator(self, validator: str, reward: int) -> None:
        """
            Reward a validator with the given amount of wei
            This doesn't update the effective balance of the validator
            A later call to process_effective_balance_updates is required
        """
        self._balances[validator] += reward

    def penalize_validator(self, validator: str, penalty: int) -> None:
        """
            Penalize a validator with the given amount of wei
            This doesn't update the effective balance of the validator
            A later call to process_effective_balance_updates is required
        """
        self._balances[validator] -= penalty

    def process_effective_balance_updates(self) -> None:
        """
            Process the effective balance updates for all validators in the state
            This function should be called after all rewards and penalties have been applied
            It will update the effective balance of all validators in the state
        """
        for validator in self._validators:
            balance = self._balances[validator]
            effective_balance = self._effective_balances[validator]

            if (balance + DOWNWARD_THRESHOLD < effective_balance or effective_balance + UPWARD_THRESHOLD < balance):
                self._effective_balances[validator] = min(balance - balance % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)

    def get_total_effective_balance(self) -> int:
        """
            Returns the total effective balance of all validators in the state
        """
        return sum(self._effective_balances.values())
    
    def get_validator_share(self, validator: str) -> float:
        """
            Returns the share of the total effective balance of the given validator
        """
        assert validator in self._validators

        return self._effective_balances[validator] / self.get_total_effective_balance()
    
    def get_base_reward_per_increment(self) -> int:
        """
            Returns the base reward per increment
        """
        return EFFECTIVE_BALANCE_INCREMENT * BASE_REWARD_FACTOR // int(math.sqrt(self.get_total_effective_balance()))
    
    def get_base_reward(self, validator: str) -> int:
        """
            Returns the base reward for the given validator
        """
        assert validator in self._validators

        increments = self._effective_balances[validator] // EFFECTIVE_BALANCE_INCREMENT
        return increments * self.get_base_reward_per_increment()

    def get_participation(self, epoch: int, flag_index: str) -> list[str]:

        """
            Returns the list of active validators that participated in the given epoch
        """

        assert epoch in [self.current_epoch(), self.previous_epoch()]

        active_validators = self.get_active_validators(epoch)

        if epoch == self.current_epoch():
            epoch_participation = self._current_participations
        
        else:
            epoch_participation = self._previous_participations

        participations = []

        def has_flag(participation: int, flag_index: int) -> bool:
            bit_flag = 2 ** flag_index
            return participation & bit_flag == bit_flag

        for participant, participation in epoch_participation.items():
            if has_flag(participation, flag_index) and participant in active_validators:
                participations.append(participant)

        return participations
    
    def get_group_effective_balance(self, validators: list[str]) -> int:
        """
            Returns the total effective balance of the given validators
        """
        return sum([self._effective_balances[validator] for validator in validators])
    
    def register_participation(self, validator: str, flag_index: int) -> None:
        """
            Register the participation of the given validator in the current epoch
        """
        assert validator in self._validators

        self.current_epoch_participation[validator] |= flag_index

    def get_active_validators(self, epoch: int) -> list[str]:
        """
            Returns the list of active validators in the given epoch
            TODO: implement the validator class to account for activation and exit epochs
            as well as slahed validators
        """
        return self._validators
    
    def get_eligible_validators(self) -> list[str]:
        """
            Returns the list of eligible validators
            TODO: implement the validator class to account for activation and exit epochs
        """
        return self._validators
    
    @property
    def justification_bits(self) -> BitVector:
        """
            Returns the justification bits of the state
        """
        return self._justification_bits
    
    @justification_bits.setter
    def justification_bits(self, justification_bits: BitVector) -> None:
        """
            Sets the justification bits of the state
        """
        self._justification_bits = justification_bits

    @property
    def previous_epoch_participation(self) -> dict[str, int]:
        """
            Returns the previous epoch participation of the state
        """
        return self._previous_participations
    
    @previous_epoch_participation.setter
    def previous_epoch_participation(self, previous_epoch_participation: dict[str, int]) -> None:
        """
            Sets the previous epoch participation of the state
        """
        self._previous_participations = previous_epoch_participation

    @property
    def current_epoch_participation(self) -> dict[str, int]:
        """
            Returns the current epoch participation of the state
        """
        return self._current_participations
    
    @current_epoch_participation.setter
    def current_epoch_participation(self, current_epoch_participation: dict[str, int]) -> None:
        """
            Sets the current epoch participation of the state
        """
        self._current_participations = current_epoch_participation

    def get_finality_delay(self) -> int:
        """
            Get the finality delay of the state
        """
        return self.previous_epoch() - self._finalized_checkpoint.slot // SLOTS_PER_EPOCH

    def is_in_inactivity_leak(self) -> bool:
        """
            Returns true if the state is in inactivity leak
        """              
        return self.get_finality_delay() > MIN_EPOCHS_TO_INACTIVITY_PENALTY

    def process_participation_flag_updates(self) -> None:
        """
            Rotate the epoch participation flags
        """
        self.previous_epoch_participation = self.current_epoch_participation
        self.current_epoch_participation = { validator: 0 for validator in self.validators }

    def copy(self) -> "BeaconState":
        """
            Returns a copy of the state
        """
        return self.from_serialized(self.serialize())