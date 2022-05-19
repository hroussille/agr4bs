
"""
    Test suite for the RemoveBalance class
"""

from agr4bs.state import RemoveBalance
from agr4bs.state.state_change import StateChangeType


def test_remove_balance_state_change_type():
    """
        Test that a RemoveBalance StateChange has the correct type
    """
    change = RemoveBalance("account_name", 0)

    assert change.type == StateChangeType.REMOVE_BALANCE


def test_remove_balance_state_change():
    """
        Test that the properties of a RemoveBalance StateChangee are
        all present and accessibles.
    """

    change = RemoveBalance("account_name", 1)

    assert change.account_name == "account_name"
    assert change.value == 1


def test_remove_balance_state_change_revert():
    """
        Test that reverting a RemoveBalance StateChange yields a
        AddBalance StateChange with the same properties as the
        initial RemoveBalance StateChange.
    """

    change = RemoveBalance("account_name", 1)

    reverted = change.revert()

    assert reverted.type == StateChangeType.ADD_BALANCE
    assert reverted.account_name == change.account_name
    assert reverted.value == change.value
