
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
from agr4bs.common import export


class CustomCaller(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def custom_caller_function(agent: InternalAgent, to: str, value: int):
        agent.set_storage_at("value", value)
        calldata = InternalAgentCalldata(
            "custom_callee_function", value=value + 1)
        return agent.call(to, calldata)

    @staticmethod
    @export
    def get_value(agent: InternalAgent):
        return Success(value=agent.get_storage_at("value"))

    @staticmethod
    @export
    def depth_bomb(agent: InternalAgent):
        calldata = InternalAgentCalldata("depth_bomb")
        return agent.call(agent.name, calldata)

    @staticmethod
    @export
    def reentrency(agent: InternalAgent):

        if agent.get_storage_at("reentrency_guard") is True:
            return Revert(agent.name + " : Reentrency guard")

        agent.set_storage_at("reentrency_guard", True)

        calldata = InternalAgentCalldata("reentrency")
        response = agent.call(agent.name, calldata)

        agent.set_storage_at("reentrency_guard", False)

        return response


class CustomCallee(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def custom_callee_function(agent: InternalAgent, value: int):

        calldata = InternalAgentCalldata("get_value")
        response = agent.call(agent.ctx.caller, calldata, 0)

        if response.reverted is True:
            return response

        agent.set_storage_at("value", response.return_value["value"] + value)
        return Success()


def test_simple_call():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()

    caller_agent = agr4bs.InternalAgent("account_1")
    caller_agent.add_role(CustomCaller())

    callee_agent = agr4bs.InternalAgent("account_2")
    callee_agent.add_role(CustomCallee())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=caller_agent)
    account_2 = Account("account_2", internal_agent=callee_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.CreateAccount(account_2),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentCalldata(
        "custom_caller_function", value=1, to="account_2").serialize())
    tx = agr4bs.ITransaction("account_0", "account_1",
                            0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.get_account_storage_at("account_1", "value") == 1
    assert state.get_account_storage_at("account_2", "value") == 3


def test_depth_limit():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()

    caller_agent = agr4bs.InternalAgent("account_1")
    caller_agent.add_role(CustomCaller())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=caller_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1)]

    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentCalldata("depth_bomb").serialize())
    tx = agr4bs.ITransaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is True
    assert receipt.revert_reason == "VM : Max call depth exceeded"


def test_reentrency():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()

    caller_agent = agr4bs.InternalAgent("account_1")
    caller_agent.add_role(CustomCaller())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=caller_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1)]

    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentCalldata("reentrency").serialize())
    tx = agr4bs.ITransaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is True
    assert receipt.revert_reason == "account_1 : Reentrency guard"
