"""
    Storage file class implementation
"""

from typing import NamedTuple
from ..blockchain import Transaction
from .state_change import StateChange

class Receipt(NamedTuple):

    """
        Receipt keeps track of the outcome of a Transaction execution.
        Such as gas comsumption, success or revert of the Transaction and
        all StateChange required to apply or revert the Transaction.
    """

    tx: Transaction
    state_changes: list[StateChange]
    reverted: bool
    revert_reason: str

    def __str__(self):
        str = f"[Receipt] hash : {self.tx.hash} reverted: {self.reverted}"

        if self.reverted:
            str = str + f" reason: {self.revert_reason}"

        str += " state_changes: "

        for state_change in self.state_changes:
            str += f"{state_change.__str__()} "

        return str


