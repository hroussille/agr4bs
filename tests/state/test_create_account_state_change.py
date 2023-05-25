
"""
    Test suite for the CreateAccount class
"""

from agr4bs.state import Account, CreateAccount
from agr4bs.state.state_change import StateChangeType


def test_create_account_state_change_type():
    """
        Test that a CreateAccount StateChange has the correct type
    """
    new_account = Account("account_name")
    change = CreateAccount(new_account)

    assert change.type == StateChangeType.CREATE_ACCOUNT


def test_create_account_state_change():
    """
        Test that the properties of a CreateAccount StateChangee are
        all present and accessibles.
    """

    nonce = 10
    balance = 100
    internal_agent = None
    storage = {"key": "value"}

    new_account = Account("account_name", balance,
                          nonce, internal_agent, storage)

    change = CreateAccount(new_account)

    assert change.account_name == "account_name"
    assert change.account.nonce == nonce
    assert change.account.internal_agent == internal_agent
    assert change.account.storage == storage


def test_create_account_state_change_revert():
    """
        Test that reverting a CreateAccount StateChange yields a
        DeleteAccount StateChange with the same properties as the
        initial CreateAccount StateChange.
    """
    nonce = 10
    balance = 100
    internal_agent = None
    storage = {"key": "value"}

    new_account = Account("account_name", balance,
                          nonce, internal_agent, storage)

    change = CreateAccount(new_account)

    reverted = change.revert()

    assert reverted.type == StateChangeType.DELETE_ACCOUNT
    assert reverted.account_name == change.account_name
    assert reverted.account.nonce == change.account.nonce
    assert reverted.account.internal_agent == change.account.internal_agent
    assert reverted.account.storage == storage
