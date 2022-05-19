"""
    Test suite for the IncrementAccountNonce class
"""

from agr4bs.state import IncrementAccountNonce
from agr4bs.state.state_change import StateChangeType


def test_increment_account_nonce_state_change_type():
    """
         Test that an IncrementAcccountNonce StateChange has the correct type
    """
    change = IncrementAccountNonce("account name")

    assert change.type == StateChangeType.INCREMENT_ACCOUNT_NONCE


def test_increment_account_nonce_state_change_properties():
    """
        Test that the properties of an IncrementAccountNonce StateChangee are
        all present and accessibles.
    """
    change = IncrementAccountNonce("account name")

    assert change.account_name == "account name"


def test_increment_account_nonce_state_change_revert():
    """
        Test that reverting an IncrementAccountNonce StateChange yields a
        DecrementAccountNonce StateChange with the same properties as the
        initial IncrementAccountNonce StateChange.
    """
    change = IncrementAccountNonce("account name")

    reverted = change.revert()

    assert reverted.type == StateChangeType.DECREMENT_ACCOUNT_NONCE
    assert reverted.account_name == change.account_name
