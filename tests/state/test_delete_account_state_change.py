
"""
    Test suite for the DeleteAccount class
"""

from agr4bs.state import Account, DeleteAccount
from agr4bs.state.state_change import StateChangeType


def test_delete_account_state_change_type():
    """
        Test that a DeleteAccount StateChange has the correct type
    """
    deleted_account = Account("account_name")
    change = DeleteAccount(deleted_account)

    assert change.type == StateChangeType.DELETE_ACCOUNT


def test_delete_account_state_change():
    """
        Test that the properties of a DeleteAccount StateChangee are
        all present and accessibles.
    """

    nonce = 10
    balance = 100
    internal_agent = None
    storage = {"key": "value"}

    deleted_account = Account("account_name", balance,
                              nonce, internal_agent, storage)
    change = DeleteAccount(deleted_account)

    assert change.account_name == "account_name"
    assert change.account.nonce == nonce
    assert change.account.internal_agent == internal_agent
    assert change.account.storage == storage


def test_delete_account_state_change_revert():
    """
        Test that reverting a DeleteAccount StateChange yields a
        CreateAccount StateChange with the same properties as the
        initial DeleteAccount StateChange.
    """
    nonce = 10
    balance = 100
    internal_agent = None
    storage = {"key": "value"}

    deleted_account = Account("account_name", balance,
                              nonce, internal_agent, storage)
    change = DeleteAccount(deleted_account)

    reverted = change.revert()

    assert reverted.type == StateChangeType.CREATE_ACCOUNT
    assert reverted.account_name == change.account_name
    assert reverted.account.nonce == change.account.nonce
    assert reverted.account.internal_agent == change.account.internal_agent
    assert reverted.account.storage == storage
