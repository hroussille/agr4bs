"""
Constants for the Eth2 specification.
"""

# Number of seconds in a slot
SLOT_TIME = 12
INTERVAL_PER_SLOT = 3

# Number of slots in an epoch
SLOTS_PER_EPOCH = 32

# Initial Epoch
GENESIS_EPOCH = 0

# Default balance (in wei) for new validators
NEW_VALIDATOR_BALANCE = 32 * 10 ** 9  # Gwei
MAX_EFFECTIVE_BALANCE = 32 * 10 ** 9  # Gwei
EFFECTIVE_BALANCE_INCREMENT = 10 ** 9  # Gwei

# Hysteresis parameters for the effective balance calculation
HYSTERESIS_QUOTIENT = 4
HYSTERESIS_DOWNWARD_MULTIPLIER = 1
HYSTERESIS_UPWARD_MULTIPLIER = 5
HYSTERESIS_INCREMENT = int(EFFECTIVE_BALANCE_INCREMENT // HYSTERESIS_QUOTIENT)
DOWNWARD_THRESHOLD = int(HYSTERESIS_INCREMENT * HYSTERESIS_DOWNWARD_MULTIPLIER)
UPWARD_THRESHOLD = int(HYSTERESIS_INCREMENT * HYSTERESIS_UPWARD_MULTIPLIER)

# Rewards constants
BASE_REWARD_FACTOR = 64
BASE_REWARD_PER_EPOCH = 4
TIMELY_SOURCE_WEIGHT = 14
TIMELY_TARGET_WEIGHT = 26
TIMELY_HEAD_WEIGHT = 14
SYNC_REWARD_WEIGHT = 2
PROPOSER_WEIGHT = 8
WEIGHT_DENOMINATOR = 64

# Proposer boost
PROPOSER_SCORE_BOOST = 40

# Bouncing attacks constants
SAFE_SLOTS_TO_UPDATE_JUSTIFIED = 8

# Participation flags
TIMELY_SOURCE_FLAG_INDEX = 0
TIMELY_TARGET_FLAG_INDEX = 1
TIMELY_HEAD_FLAG_INDEX = 2

# Justification bits
JUSTIFICATION_BITS_LENGTH = 4
 
MIN_ATTESTATION_INCLUSION_DELAY = 1

PARTICIPATION_FLAG_WEIGHTS = [TIMELY_SOURCE_WEIGHT, TIMELY_TARGET_WEIGHT, TIMELY_HEAD_WEIGHT]
MIN_EPOCHS_TO_INACTIVITY_PENALTY = 4

INACTIVITY_PENALTY_QUOTIONT = 2**26
INACTIVITY_PENALTY_QUOTIENT_ALTAIR = 3 * 2**24
INACTIVITY_PENALTY_QUOTIENT_BELLATRIX = 2 ** 24

INACTIVITY_SCORE_BIAS = 4
INACTIVITY_SCORE_RECOVERY_RATE = 16
