
"""
    Test suite for the State class
"""

import pytest
from deepdiff import DeepDiff, Delta
import agr4bs
from agr4bs.state import Account
from agr4bs.state.state_change import CreateAccount, DeleteAccount, UpdateAccountStorage
from agr4bs.state.state_change import AddBalance, RemoveBalance


def test_state_initial_state():
    """
        Test that a State is initially empty
        except for the genesis account
    """
    state = agr4bs.State()

    assert state.account_names() == ['genesis']


def test_state_create_account_change():
    """
        Test that a State can apply a CreateAccount StateChange
        and that the Account can be retrived from the State
    """
    state = agr4bs.State()
    new_account = Account("new_account")
    state.apply_state_change(CreateAccount(new_account))

    assert state.get_account("new_account") is not None
    assert state.get_account_nonce("new_account") == 0
    assert state.get_account_balance("new_account") == 0


def test_state_create_account_change_conflict():
    """
        Test that a State raises a ValueError if any attempt is made
        to create an Account with the same name as an existing one.
    """
    state = agr4bs.State()
    new_account = Account("new_account")
    state.apply_state_change(CreateAccount(new_account))

    with pytest.raises(ValueError) as excinfo:
        state.apply_state_change(CreateAccount(new_account))
        assert "Cannot create already existing Account" in str(excinfo.value)


def test_state_delete_account_change():
    """
        Test that a State can apply a DeleteAccount StateChange
        and that the Account is effectively removed from the State
    """
    state = agr4bs.State()

    new_account = Account("new_account")
    state.apply_state_change(CreateAccount(new_account))
    state.apply_state_change(DeleteAccount(new_account))

    assert state.get_account("new_account") is None
    assert state.get_account_nonce("new_account") == 0
    assert state.get_account_balance("new_account") == 0


def test_state_delete_account_change_conflict():
    """
        Test that a State raises a ValueError if any attempt is made
        to delete an Account that does not exist.
    """
    state = agr4bs.State()

    new_account = Account("new_account")
    state.apply_state_change(CreateAccount(new_account))
    state.apply_state_change(DeleteAccount(new_account))

    with pytest.raises(ValueError) as excinfo:
        state.apply_state_change(DeleteAccount(new_account))
        assert "Cannot delete non existing Account" in str(excinfo.value)


def test_state_add_balance_change():
    """
        Test that a State can apply a AddBalance StateChange
        and that the Account balance change is written to the
        State
    """
    state = agr4bs.State()

    new_account = Account("new_account")
    state.apply_state_change(CreateAccount(new_account))
    state.apply_state_change(AddBalance("new_account", value=10))

    assert state.get_account_balance("new_account") == 10


def test_state_add_balance_change_no_account():
    """
        Test that a State raises a ValueError if any attempt is made
        to add to the balance of a non existing Account.
    """
    state = agr4bs.State()

    with pytest.raises(ValueError) as excinfo:
        state.apply_state_change(AddBalance("new_account", value=10))
        assert "Cannot add balance to non existing Account" in str(
            excinfo.value)


def test_state_remove_balance_change():
    """
        Test that a State can apply a RemoveBalance StateChange
        and that the Account balance change is written to the
        State
    """
    state = agr4bs.State()

    new_account = Account("new_account", balance=10)
    state.apply_state_change(CreateAccount(new_account))
    state.apply_state_change(RemoveBalance("new_account", value=10))

    assert state.get_account_balance("new_account") == 0


def test_state_remove_balance_change_no_account():
    """
        Test that a State raises a ValueError if any attempt is made
        to remove from the balance of a non existing Account.
    """
    state = agr4bs.State()

    with pytest.raises(ValueError) as excinfo:
        state.apply_state_change(RemoveBalance("new_account", value=10))
        assert "Cannot remove balance from non existing Account" in str(
            excinfo.value)


def test_state_update_account_storage_change():
    """
        Test that a State can apply a UpdateStorage StateChange
        and that the Account storage change is written to the
        State
    """
    state = agr4bs.State()

    new_account = Account("new_account")
    new_storage = {'key': 'value'}

    delta_apply = Delta(DeepDiff(new_account.storage, new_storage))
    delta_revert = Delta(DeepDiff(new_storage, new_account.storage))

    state.apply_state_change(CreateAccount(new_account))
    state.apply_state_change(UpdateAccountStorage(
        "new_account", delta_apply, delta_revert))

    assert state.get_account_storage("new_account") == new_storage


def test_state_update_account_storage_change_no_account():
    """
        Test that a State raises a ValueError if any attempt is made
        to update the storage of a non existing Account.
    """
    state = agr4bs.State()
    old_storage = {}
    new_storage = {'key': 'value'}

    delta_apply = Delta(DeepDiff(old_storage, new_storage))
    delta_revert = Delta(DeepDiff(new_storage, old_storage))

    with pytest.raises(ValueError) as excinfo:
        state.apply_state_change(UpdateAccountStorage(
            "new_account", delta_apply, delta_revert))
        assert "Cannot update storage of non existing Account" in str(
            excinfo.value)


def test_state_get_account():
    """
        Test that an existing Account can be retrived from the State
    """
    state = agr4bs.State()
    new_account = Account("new_account", balance=10,
                          nonce=1, storage={"key": "value"})

    state.apply_state_change(CreateAccount(new_account))
    account = state.get_account("new_account")

    assert account is not None
    assert account.name == "new_account"
    assert account.nonce == 1
    assert account.balance == 10
    assert account.storage == {"key": "value"}


def test_state_get_account_no_account():
    """
        Test that retrieving a non existing Account from the State
        yields None
    """
    state = agr4bs.State()

    assert state.get_account("new_account") is None


def test_state_get_account_balance():
    """
        Test that the balance of an existing Account can be retrived
        from the State
    """
    state = agr4bs.State()

    new_account = Account("new_account", balance=10)
    state.apply_state_change(CreateAccount(new_account))

    assert state.get_account_balance("new_account") == 10


def test_state_get_account_balance_no_account():
    """
        Test that retriving a non existing Account balance from
        the State yields 0
    """
    state = agr4bs.State()

    assert state.get_account_balance("new_account") == 0


def test_state_get_account_nonce():
    """
        Test that the nonce of an existing Account can be retrived
        from the State
    """
    state = agr4bs.State()

    new_account = Account("new_account", nonce=1)
    state.apply_state_change(CreateAccount(new_account))

    assert state.get_account_nonce("new_account") == 1


def test_state_get_account_nonce_no_account():
    """
        Test that retrieving a non existing Account nonce from
        the State yields 0
    """
    state = agr4bs.State()

    assert state.get_account_nonce("new_account") == 0


def test_state_get_account_storage():
    """
        Test that the storage of an existing Account can be retrived from
        the State
    """
    state = agr4bs.State()
    storage = {"key": "value"}

    new_account = Account("new_account", storage=storage)
    state.apply_state_change(CreateAccount(new_account))
    assert state.get_account_storage("new_account") == storage


def test_state_get_account_storage_no_account():
    """
        Test that retrieving a non existing Account storage from
        the State yields None
    """
    state = agr4bs.State()

    assert state.get_account_storage("new_account") is None


def test_state_get_account_storage_at():
    """
        Test that the storage at a specific key of an Account can be
        retrived from the State
    """
    state = agr4bs.State()
    storage = {"key": "value"}

    new_account = Account("new_account", storage=storage)
    state.apply_state_change(CreateAccount(new_account))

    assert state.get_account_storage_at("new_account", "key") == "value"


def test_state_get_account_storage_at_no_account():
    """
        Test that retrieving the storage at a specific key of a non
        existing Account yields None
    """
    state = agr4bs.State()

    assert state.get_account_storage_at("new_account", "key") is None


def test_state_get_account_internal_agent():
    """
        Test that the InternalAgent of an existing Account can be
        retrieved from the State
    """
    state = agr4bs.State()
    agent = agr4bs.InternalAgent("new_account")

    new_account = Account("new_account", internal_agent=agent)
    state.apply_state_change(CreateAccount(new_account))

    _agent = state.get_account_internal_agent("new_account")

    assert _agent.name == agent.name


def test_state_get_account_internal_agent_no_account():
    """
        Test that retrieving a non existant InternalAgent from
        the State yields None
    """
    state = agr4bs.State()

    assert state.get_account_internal_agent("new_account") is None
