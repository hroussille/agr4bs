"""
    Storage file class implementation
"""

from typing import NamedTuple
from .state_change import StateChange


class Receipt(NamedTuple):

    """
        Receipt keeps track of the outcome of a Transaction execution.
        Such as gas comsumption, success or revert of the Transaction and
        all StateChange required to apply or revert the Transaction.
    """

    tx_hash: str
    state_changes: list[StateChange]
    reverted: bool
