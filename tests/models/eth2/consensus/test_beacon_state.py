
from agr4bs.models.eth2.blockchain import Block
from agr4bs.models.eth2.consensus import BeaconState
from agr4bs.models.eth2.constants import *

def test_beacon_state_initialization():
    """
    Ensures that a BeaconState is correctly initialized
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    assert state.current_epoch() == 0
    assert state.current_slot() == 0
    assert state.latest_block() == genesis
    assert state.current_justified_checkpoint() == genesis
    assert state.previous_justified_checkpoint() == genesis
    assert state.finalized_checkpoint() == genesis

def test_beacon_state_add_validator():
    """
    Ensures that a validator is correctly added to the state
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")

    assert state.validators == ["agent_0"]
    assert state.balances == {"agent_0": NEW_VALIDATOR_BALANCE}
    assert state.effective_balances == {"agent_0": MAX_EFFECTIVE_BALANCE}

def test_beacon_state_total_active_balance():
    """
    Ensures that the total active balance is correctly computed
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.add_validator("agent_1")

    assert state.get_total_effective_balance() == 2 * MAX_EFFECTIVE_BALANCE

def test_beacon_state_reward_validator():
    """
    Ensures that the validator is correctly rewarded
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.reward_validator("agent_0", 1)

    assert state.balances["agent_0"] == NEW_VALIDATOR_BALANCE + 1
    assert state.effective_balances["agent_0"] == MAX_EFFECTIVE_BALANCE

def test_beacon_state_penalize_validator():
    """
    Ensures that the validator is correctly penalized
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.penalize_validator("agent_0", 1)

    assert state.balances["agent_0"] == NEW_VALIDATOR_BALANCE - 1
    assert state.effective_balances["agent_0"] == MAX_EFFECTIVE_BALANCE

def test_beacon_state_process_effective_balance_updates_downward_no_threshold():
    """
    Ensures that the effective balances are correctly updated
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.penalize_validator("agent_0", DOWNWARD_THRESHOLD)
    state.process_effective_balance_updates()

    # Too low of a penalty to be reflected in the effective balance
    assert state.balances["agent_0"] == NEW_VALIDATOR_BALANCE - DOWNWARD_THRESHOLD
    assert state.effective_balances["agent_0"] == NEW_VALIDATOR_BALANCE

def test_beacon_state_process_effective_balance_updates_downward_threshold():
    """
    Ensures that the effective balances are correctly updated
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.penalize_validator("agent_0", DOWNWARD_THRESHOLD + 1)
    state.process_effective_balance_updates()

    # Too low of a penalty to be reflected in the effective balance
    assert state.balances["agent_0"] == NEW_VALIDATOR_BALANCE - DOWNWARD_THRESHOLD - 1
    assert state.effective_balances["agent_0"] == NEW_VALIDATOR_BALANCE - EFFECTIVE_BALANCE_INCREMENT

def test_beacon_state_process_effective_balance_updates_upward_max_effective():
    """
    Ensures that the effective balances are correctly updated
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    state.add_validator("agent_0")
    state.reward_validator("agent_0", 1)
    state.process_effective_balance_updates()

    # Too high of a reward to be reflected in the effective balance
    # Effective balance is capped at MAX_EFFECTIVE_BALANCE
    assert state.balances["agent_0"] == NEW_VALIDATOR_BALANCE + 1
    assert state.effective_balances["agent_0"] == MAX_EFFECTIVE_BALANCE

def test_beacon_state_process_effective_balance_updates_upward_no_threshold():
    """
    Ensures that the effective balances are correctly updated
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    # Bring the validator to 30 ETH of effective balance
    state.add_validator("agent_0")
    state.penalize_validator("agent_0", 2 * EFFECTIVE_BALANCE_INCREMENT)
    state.process_effective_balance_updates()

    assert state.balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT
    assert state.effective_balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT

    # Increase the validator's balance by 1.25 ETH : just under the threshold for an effective balance increase
    state.reward_validator("agent_0", 5 * EFFECTIVE_BALANCE_INCREMENT // 4)
    state.process_effective_balance_updates()

    assert state.balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT + 5 * EFFECTIVE_BALANCE_INCREMENT // 4
    assert state.effective_balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT

def test_beacon_state_process_effective_balance_updates_upward_hreshold():
    """
    Ensures that the effective balances are correctly updated
    """
    genesis = Block(None, None, 0, [])

    genesis.justified = True
    genesis.finalized = True

    state = BeaconState(genesis)

    # Bring the validator to 30 ETH of effective balance
    state.add_validator("agent_0")
    state.penalize_validator("agent_0", 2 * EFFECTIVE_BALANCE_INCREMENT)
    state.process_effective_balance_updates()

    assert state.balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT
    assert state.effective_balances["agent_0"] == 30 * EFFECTIVE_BALANCE_INCREMENT

    # Increase the validator's balance by 1.25 ETH  + 1 wei: just above the threshold for an effective balance increase
    state.reward_validator("agent_0", 1 + 5 * EFFECTIVE_BALANCE_INCREMENT // 4)
    state.process_effective_balance_updates()

    assert state.balances["agent_0"] == 1 + 30 * EFFECTIVE_BALANCE_INCREMENT + 5 * EFFECTIVE_BALANCE_INCREMENT // 4
    assert state.effective_balances["agent_0"] == 31 * EFFECTIVE_BALANCE_INCREMENT