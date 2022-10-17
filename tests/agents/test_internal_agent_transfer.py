
"""
    Test suite for the VM class
"""

import agr4bs
from agr4bs.agents import InternalAgent, AgentType
from agr4bs.agents.internal_agent import InternalAgentCalldata
from agr4bs.blockchain.payload import Payload
from agr4bs.roles import RoleType
from agr4bs.state import Account
from agr4bs.common import export, payable


class CustomTransfer(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    @payable
    def custom_transfer_function(agent: InternalAgent, to: str, value: int):
        return agent.transfer(to, value)


def test_simple_transfer():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()

    transfer_agent = agr4bs.InternalAgent("account_1")
    transfer_agent.add_role(CustomTransfer())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=transfer_agent)
    account_2 = Account("account_2")

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.CreateAccount(account_2),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentCalldata("custom_transfer_function", value=100, to="account_2").serialize())
    tx = agr4bs.Transaction("account_0", "account_1", 0, payload=payload, value=100)
    vm = agr4bs.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.get_account_balance("account_0") == 0
    assert state.get_account_balance("account_1") == 0
    assert state.get_account_balance("account_2") == 100