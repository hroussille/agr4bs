
"""
    Test suite for the AddBalance class
"""

from agr4bs.state import AddBalance
from agr4bs.state.state_change import StateChangeType


def test_add_balance_state_change_type():
    """
        Test that a AddBalance StateChange has the correct type
    """
    change = AddBalance("account_name", 0)

    assert change.type == StateChangeType.ADD_BALANCE


def test_add_balance_state_change():
    """
        Test that the properties of a AddBalance StateChangee are
        all present and accessibles.
    """

    change = AddBalance("account_name", 1)

    assert change.account_name == "account_name"
    assert change.value == 1


def test_add_balance_state_change_revert():
    """
        Test that reverting a AddBalance StateChange yields a
        RemoveBalance StateChange with the same properties as the
        initial AddBalance StateChange.
    """

    change = AddBalance("account_name", 1)

    reverted = change.revert()

    assert reverted.type == StateChangeType.REMOVE_BALANCE
    assert reverted.account_name == change.account_name
    assert reverted.value == change.value
