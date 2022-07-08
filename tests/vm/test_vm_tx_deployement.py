
import agr4bs
from agr4bs.agents import InternalAgent, AgentType
from agr4bs.agents import Success, Revert
from agr4bs.agents.internal_agent import InternalAgentCalldata, InternalAgentDeployement
from agr4bs.blockchain.payload import Payload
from agr4bs.roles import RoleType
from agr4bs.state import Account
from agr4bs.common import export, payable


class RoleWithConstructor(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(agent: InternalAgent):
        agent.set_storage_at("key", "value")
        return Success()

    @staticmethod
    @export
    def custom_function(agent: InternalAgent):
        return Success(key=agent.get_storage_at("key"))


class RoleWithConstructorAndParameters(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(agent: InternalAgent, value):
        agent.set_storage_at("key", value)
        return Success()

    @staticmethod
    @export
    def custom_function(agent: InternalAgent):
        return Success(key=agent.get_storage_at("key"))


class RoleWithoutConstructor(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def custom_function(agent: InternalAgent):
        return Success(key=agent.get_storage_at("key"))


def test_deploy_with_constructor():
    """
        Test that the VM returns the correct StateChange on a single
        call when the callee has no accoutn associated to it
    """

    state = agr4bs.State()
    account_0 = Account("account_0")
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(RoleWithConstructor())

    changes = [agr4bs.state.CreateAccount(account_0)]
    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentDeployement(internal_agent).serialize())
    tx = agr4bs.Transaction("account_0", None, 0, payload=payload)
    vm = agr4bs.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False
    assert receipt.revert_reason is None

    state.apply_batch_state_change(receipt.state_changes)

    assert state.get_account_storage_at("account_1", "key") == "value"

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata("custom_function").serialize())
    tx = agr4bs.Transaction("account_0", "account_1", 1, payload=payload)

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False


def test_deploy_without_constructor():
    """
        Test that the VM returns the correct StateChange on a single
        call when the callee has no accoutn associated to it
    """

    state = agr4bs.State()
    account_0 = Account("account_0")
    internal_agent = agr4bs.InternalAgent("account_1")
    internal_agent.add_role(RoleWithoutConstructor())

    changes = [agr4bs.state.CreateAccount(account_0)]
    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentDeployement(internal_agent).serialize())
    tx = agr4bs.Transaction("account_0", None, 0, payload=payload)
    vm = agr4bs.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False
    assert receipt.revert_reason is None

    state.apply_batch_state_change(receipt.state_changes)

    assert state.has_account("account_1")
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_nonce("account_1") == 0

    payload = Payload(InternalAgentCalldata("custom_function").serialize())
    tx = agr4bs.Transaction("account_0", "account_1", 1, payload=payload)

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False
