
"""
    Test suite for the VM class
"""

import agr4bs
from agr4bs.agents import InternalAgent, AgentType
from agr4bs.agents import Success, Revert
from agr4bs.agents.internal_agent import InternalAgentCalldata
from agr4bs.blockchain.payload import Payload
from agr4bs.roles import RoleType
from agr4bs.state import Account
from agr4bs.common import export, payable


class CustomInternalAgentRole(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    def constructor(self):
        super().constructor()

    @staticmethod
    @export
    def custom_non_payable_function(agent: InternalAgent):
        return Success()

    @staticmethod
    @export
    @payable
    def custom_payable_function(agent: InternalAgent):
        return Success()

    @staticmethod
    @export
    @payable
    def custom_payable_return_function(agent: InternalAgent):
        return Success(value=agent.ctx.value)

    @staticmethod
    @export
    def custom_state_changing_function(agent: InternalAgent):
        agent.set_storage_at("key", "value")
        return Success()

    @staticmethod
    @export
    def custom_reverting_function(agent: InternalAgent):
        return Revert("Always revert")


def test_call_with_non_existing_account():
    """
        Test that the VM returns the correct StateChange on a single
        call when the callee has no accoutn associated to it
    """

    state = agr4bs.State()

    account_0 = Account("account_0")

    changes = [agr4bs.state.CreateAccount(account_0)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_non_payable_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is True
    assert receipt.revert_reason == "VM : No InternalAgent to call"
    assert len(receipt.state_changes) == 1

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 1


def test_call_non_payable_with_value():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a non payable function
    """

    state = agr4bs.State()
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(CustomInternalAgentRole())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=internal_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_non_payable_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1",
                            0, value=100, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is True
    assert receipt.revert_reason == "InternalAgent: Function is not payable"
    assert len(receipt.state_changes) == 1

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0


def test_call_payable_with_existing_account():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(CustomInternalAgentRole())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=internal_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_payable_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1",
                            0, value=100, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 100
    assert state.get_account_nonce("account_1") == 0


def test_call_payable_return_value_with_existing_account():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(CustomInternalAgentRole())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=internal_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_payable_return_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1",
                            0, value=100, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 0
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 100
    assert state.get_account_nonce("account_1") == 0


def test_call_with_state_changing_function():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(CustomInternalAgentRole())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=internal_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_state_changing_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    assert state.get_account_storage_at("account_1", "key") == "value"


def test_call_with_reverting_function():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(CustomInternalAgentRole())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=internal_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 0

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata(
        "custom_reverting_function").serialize())
    tx = agr4bs.models.eth1.Transaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is True
    assert receipt.revert_reason == "Always revert"

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_0")
    assert state.get_account_balance("account_0") == 100
    assert state.get_account_nonce("account_0") == 1

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0
