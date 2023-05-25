"""
    Test suite for the DecrementAccountNonce class
"""

from agr4bs.state import DecrementAccountNonce
from agr4bs.state.state_change import StateChangeType


def test_decrement_account_nonce_state_change_type():
    """
         Test that an DecrementAcccountNonce StateChange has the correct type
    """
    change = DecrementAccountNonce("account name")

    assert change.type == StateChangeType.DECREMENT_ACCOUNT_NONCE


def test_decrement_account_nonce_state_change_properties():
    """
        Test that the properties of an DecrementAccountNonce StateChangee are
        all present and accessibles.
    """
    change = DecrementAccountNonce("account name")

    assert change.account_name == "account name"


def test_decrement_account_nonce_state_change_revert():
    """
        Test that reverting an DecrementAccountNonce StateChange yields a
        IncrementAccountNonce StateChange with the same properties as the
        initial DecrementAccountNonce StateChange.
    """
    change = DecrementAccountNonce("account name")

    reverted = change.revert()

    assert reverted.type == StateChangeType.INCREMENT_ACCOUNT_NONCE
    assert reverted.account_name == change.account_name
