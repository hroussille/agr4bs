
"""
    Test suite for the Account class
"""

import agr4bs


def test_account_default_properties():
    """
        Test the default values for optional properties of Account
        balance : 0
        nonce : 0
        internal_agent : None
    """

    account = agr4bs.Account("name")

    assert account.name == "name"
    assert account.balance == 0
    assert account.nonce == 0
    assert account.internal_agent is None
    assert account.storage == {}


def test_account_balance():
    """
        Test the given property balance of an Account
    """

    account = agr4bs.Account("name", balance=1)
    assert account.balance == 1


def test_account_nonce():
    """
        Test the given property nonce of an Account
    """
    account = agr4bs.Account("name", nonce=1)
    assert account.nonce == 1


def test_account_internal_agent():
    """
        Test the given property internal_agent of an Account
    """
    agent = agr4bs.InternalAgent("name")
    account = agr4bs.Account(agent.name, internal_agent=agent)

    assert account.internal_agent == agent


def test_account_storage():
    """
        Test the given property storage of an Account
    """
    storage = {"key": "value"}
    account = agr4bs.Account("name", storage=storage)

    assert account.get_storage_at("key") == "value"
