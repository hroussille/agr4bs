
"""
    Test suite for the StateChange class
"""

import pytest
from agr4bs.state import StateChange
from agr4bs.state.state_change import StateChangeType


def test_state_change_type():
    """
        Test that a StateChange has the given type
    """
    change_fake_add_balance = StateChange(
        StateChangeType.ADD_BALANCE, "account_name")
    change_fake_remove_balance = StateChange(
        StateChangeType.REMOVE_BALANCE, "account_name")

    assert change_fake_add_balance.type == StateChangeType.ADD_BALANCE
    assert change_fake_remove_balance.type == StateChangeType.REMOVE_BALANCE


def test_state_change_properties():
    """
        Test that the properties of a StateChangee are
        all present and accessibles.
    """
    change_fake_add_balance = StateChange(StateChangeType.ADD_BALANCE,
                                          "account_name")

    assert change_fake_add_balance.account_name == "account_name"


def test_state_change_revert():
    """
        Test that reverting a StateChange raises a NotImplementedError
        No silent failures.
    """
    change_fake_add_balance = StateChange(StateChangeType.ADD_BALANCE,
                                          "account_name")

    with pytest.raises(NotImplementedError) as excinfo:
        change_fake_add_balance.revert()
        assert "Called revert on base StateChange class." in str(excinfo.value)
