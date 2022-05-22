
"""
    Test suite for the VM class
"""

import agr4bs
from agr4bs.state import Account


def test_transfer_with_existing_accounts():
    """
        Test that the VM returns the correct StateChange on a single
        transfer with both Accounts already present in the State
    """

    state = agr4bs.State()

    account_0 = Account("account_0")
    account_1 = Account("account_1")

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.AddBalance("account_0", 100),
               agr4bs.state.CreateAccount(account_1)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    tx = agr4bs.Transaction("account_0", "account_1", 0, amount=100)
    vm = agr4bs.VM()

    receipt = vm.process_tx(state.copy(), tx)

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 100
    assert state.get_account_nonce("account_1") == 0


def test_transfer_with_non_existing_account():
    """
        Test that the VM returns the correct StateChange on a single
        transfer with only the sender Account already present in the State
    """

    state = agr4bs.State()

    account_0 = Account("account_0")

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1") is False

    tx = agr4bs.Transaction("account_0", "account_1", 0, amount=100)
    vm = agr4bs.VM()

    receipt = vm.process_tx(state.copy(), tx)

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 100
    assert state.get_account_nonce("account_1") == 0
