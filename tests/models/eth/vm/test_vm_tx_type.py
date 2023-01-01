import agr4bs
from agr4bs.vm.vm import TransactionType


def test_tx_type_transfer():
    """
        Test that a transfer transaction is correctly identified
    """
    state = agr4bs.State()

    tx = agr4bs.ITransaction(origin="account_0", nonce=0,
                            to="account_1", value=1)

    account_0 = agr4bs.Account("account_0")

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    # pylint: disable=protected-access
    assert agr4bs.models.eth.VM._get_transaction_type(
        state, tx) == TransactionType.TRANSFER


def test_tx_type_deployement():
    """
        Test that a deployement transaction is correctly identified
    """
    state = agr4bs.State()
    agent = agr4bs.InternalAgent("internal_agent_0")
    payload = agr4bs.Payload(
        agr4bs.InternalAgentDeployement(agent).serialize())
    tx = agr4bs.ITransaction(origin="account_0", nonce=0,
                            to=None, payload=payload)

    account_0 = agr4bs.Account("account_0")

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    # pylint: disable=protected-access
    assert agr4bs.models.eth.VM._get_transaction_type(
        state, tx) == TransactionType.DEPLOYEMENT


def test_tx_type_call():
    """
        Test that a call transaction is correctly identified
    """
    state = agr4bs.State()
    agent = agr4bs.InternalAgent("internal_agent_0")
    payload = agr4bs.Payload(
        agr4bs.InternalAgentCalldata('function').serialize())
    tx = agr4bs.ITransaction(origin="account_0", nonce=0,
                            to=None, payload=payload)

    account_0 = agr4bs.Account("account_0")
    account_1 = agr4bs.Account("account_1", internal_agent=agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.AddBalance("account_0", 100),
               agr4bs.state.CreateAccount(account_1)]

    state.apply_batch_state_change(changes)

    # pylint: disable=protected-access
    assert agr4bs.models.eth.VM._get_transaction_type(
        state, tx) == TransactionType.DEPLOYEMENT


def test_tx_type_noop():
    """
        Test that a noop transaction is correctly identified
    """
    state = agr4bs.State()
    tx = agr4bs.ITransaction(origin="account_0", nonce=0, to="account_1")

    account_0 = agr4bs.Account("account_0")

    changes = [agr4bs.state.CreateAccount(account_0)]

    state.apply_batch_state_change(changes)

    # pylint: disable=protected-access
    assert agr4bs.models.eth.VM._get_transaction_type(
        state, tx) == TransactionType.NOOP
