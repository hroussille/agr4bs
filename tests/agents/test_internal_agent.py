
"""
    Test suite for the InternalAgent class
"""
import agr4bs
import pytest
from agr4bs.agents.agent import AgentType
from agr4bs.agents.internal_agent import InternalAgent
from agr4bs.common import payable, export
from agr4bs.agents import Revert, Success
from agr4bs.roles.role import RoleType
from agr4bs.state.account import Account
from agr4bs.state.state_change import CreateAccount
from agr4bs.vm import ExecutionContext


class CustomInternalAgentRole(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(self):
        return Success()

    @staticmethod
    @export
    def custom_function(agent: InternalAgent, counter):
        return Success(counter=counter * 2)

    @staticmethod
    @export
    @payable
    def custom_payable_function(agent: InternalAgent, counter):
        return Success(counter=counter * 2)

    @staticmethod
    @export
    def custom_state_changing_function(agent: InternalAgent):
        agent.set_storage_at('slot', 1)
        return Success()

    @staticmethod
    @export
    def custom_multi_parameter_function(agent: InternalAgent, counter_1,  counter_2):
        return Success(counter_1=counter_1 * 2, counter_2=counter_2*3)

    @staticmethod
    @export
    def custom_reverting_function(agent: InternalAgent):
        return Revert("Always revert")


def test_internal_agent_name():
    """
        Ensures that the name of the agent is coherent
        as it will also be the name of the account created in
        the blockchain state.
    """
    internal_agent = agr4bs.InternalAgent("internal_agent_0")
    assert internal_agent.name == "internal_agent_0"


def test_internal_agent_default_constructor():
    """
        Test the default constructor behavior
    """

    internal_agent = agr4bs.InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())

    calldata = agr4bs.InternalAgentCalldata("constructor")
    state = agr4bs.State()
    account = Account(internal_agent.name, internal_agent=internal_agent)
    state.apply_state_change(CreateAccount(account))
    context = ExecutionContext(
        "origin", "from", "internal_agent_0", 0, 0, state, agr4bs.VM)
    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is False


def test_internal_agent_default_constructor_double_call():
    """
        Test that the constructor cannot be called twice
    """
    internal_agent = agr4bs.InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())

    calldata = agr4bs.InternalAgentCalldata("constructor")
    state = agr4bs.State()
    account = Account(internal_agent.name, internal_agent=internal_agent)
    state.apply_state_change(CreateAccount(account))
    context = ExecutionContext(
        "origin", "from", "internal_agent_0", 0, 0, state, agr4bs.VM)

    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is False

    with pytest.raises(ValueError) as excinfo:
        response = internal_agent.entry_point(calldata, context)

    assert "Constructor already called" in str(excinfo.value)


def test_internal_agent_validate_function_valid():
    """
        Test that calling an existing function does not revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())

    # pylint: disable=protected-access
    assert internal_agent._validate_function('custom_function') is True


def test_internal_agent_validate_function_invalid():
    """
        Test that calling an uknown function does not revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())

    # pylint: disable=protected-access
    assert internal_agent._validate_function('invalid_function') is False


def test_internal_agent_validate_parameters_valid():
    """
        Test that calling a function with the required parameters does not revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_parameters(
        function, {'counter': 0}) is True


def test_internal_agent_validate_parameters_invalid_no_required():
    """
        Test that calling a function without the required parameters reverts
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_parameters(
        function, {'unknown_parameter': 0}) is False


def test_internal_agent_validate_parameters_invalid_additional_uknown():
    """
        Test that calling a function with at least one uknown parameter reverts
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_parameters(
        function, {'counter': 0, 'unknown_parameter': 0}) is False


def test_internal_agent_validate_value_valid_payable_positive():
    """
        Test that calling a payable function positive value does not
        revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_payable_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_value(function, 1) is True


def test_internal_agent_validate_value_valid_payable_zero():
    """
        Test that calling a payable function with 0 value does not
        revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_payable_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_value(function, 0) is True


def test_internal_agent_validate_value_valid_non_payable_zero():
    """
        Test that aalling a non payable function with 0 value does not
        revert
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_value(function, 0) is True


def test_internal_agent_validate_value_invalid_payable_negative():
    """
        Test that calling a a payable function reverts when given negative value
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_payable_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_value(function, -1) is False


def test_internal_agent_validate_value_invalid_non_payable_non_zero():
    """
        Test that calling a non payable function reverts when given non zero
        value.
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    function = getattr(internal_agent, 'custom_function')

    # pylint: disable=protected-access
    assert internal_agent._validate_value(function, -1) is False
    assert internal_agent._validate_value(function, 1) is False


def test_internal_agent_entry_point_valid():
    """
        Test that the entry point method behaves correctly with
        valid input data
    """

    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    calldata = agr4bs.InternalAgentCalldata("custom_function", counter=1)
    state = agr4bs.State()
    account = Account(internal_agent.name, internal_agent=internal_agent)
    state.apply_state_change(CreateAccount(account))

    context = ExecutionContext(
        "origin", "from", "internal_agent_0", 0, 0, state, agr4bs.VM)

    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is False
    assert response.revert_reason is None
    assert response.return_value['counter'] == 2
    assert context.changes == []


def test_internal_agent_entry_point_valid_multi_parameters():
    """
        Test that the entry point method behaves correctly with
        valid input data and multiple parameters
    """

    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    calldata = agr4bs.InternalAgentCalldata("custom_multi_parameter_function", counter_1=1, counter_2=2)
    state = agr4bs.State()
    account = Account(internal_agent.name, internal_agent=internal_agent)
    state.apply_state_change(CreateAccount(account))

    context = ExecutionContext("origin", "from", "internal_agent_0", 0, 0, state, agr4bs.VM)
    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is False
    assert response.revert_reason is None
    assert response.return_value['counter_1'] == 2
    assert response.return_value['counter_2'] == 6
    assert context.changes == []


def test_internal_agent_entry_point_valid_state_changing():
    """
        Test that the entry point method behaves correctly with
        valid input data
    """

    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    calldata = agr4bs.InternalAgentCalldata("custom_state_changing_function")
    state = agr4bs.State()
    account = Account(internal_agent.name, internal_agent=internal_agent)
    state.apply_state_change(CreateAccount(account))

    context = ExecutionContext("origin", "from", "internal_agent_0", 0, 0, state, agr4bs.VM)
    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is False
    assert response.revert_reason is None
    assert context.changes != []

    state.apply_batch_state_change(context.changes)

    assert state.get_account_storage_at(internal_agent.name, "slot") == 1
    assert state.get_account_storage(internal_agent.name) == {"slot": 1}


def test_internal_agent_entry_point_invalid_function():
    """
        Test that the entry point method returns a revert response
        when given an invalid function
    """
    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    calldata = agr4bs.InternalAgentCalldata("invalid_function")
    state = agr4bs.State()
    context = ExecutionContext("origin", "from", "to", 0, 0, state, agr4bs.VM())
    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is True
    assert response.revert_reason == "InternalAgent: Uknown function"
    assert context.changes == []


def test_internal_agent_entry_point_invalid_parameters():
    """
        Test that the entry point method returns a revert response
        when given invalid parameters.
    """

    internal_agent = InternalAgent("internal_agent_0")
    internal_agent.add_role(CustomInternalAgentRole())
    calldata = agr4bs.InternalAgentCalldata("custom_function", counter=0, invalid=False)
    state = agr4bs.State()
    context = ExecutionContext("origin", "from", "to", 0, 0, state, agr4bs.VM())
    response = internal_agent.entry_point(calldata, context)

    assert response.reverted is True
    assert response.revert_reason == "InternalAgent: Invalid parameters"
    assert context.changes == []
