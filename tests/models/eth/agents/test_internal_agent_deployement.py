
"""
    Test suite for the VM class
"""

import agr4bs
from agr4bs.agents import InternalAgent, AgentType
from agr4bs.agents.internal_agent import InternalAgentCalldata, InternalAgentDeployement, Success
from agr4bs.blockchain.payload import Payload
from agr4bs.roles import RoleType
from agr4bs.state import Account
from agr4bs.common import export


class CustomDeployer(agr4bs.Role):

    """
        Test call implementing a custom smart contract
    """

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def custom_deploy_function(agent: InternalAgent):
        to_deploy = InternalAgent("account_2")
        to_deploy.add_role(CustomDeployed())
        deployement = InternalAgentDeployement(to_deploy, value="value")
        return agent.deploy(deployement)

class CustomDeployed(agr4bs.Role):

    def __init__(self):
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(agent: InternalAgent, value: int):
        agent.set_storage_at("key", value)
        return Success()


def test_simple_transfer():
    """
        Test that the VM returns the correct StateChange on a single
        call with both accounts existing and value sent to a payable function
    """

    state = agr4bs.State()

    deployer_agent = agr4bs.InternalAgent("account_1")
    deployer_agent.add_role(CustomDeployer())

    account_0 = Account("account_0")
    account_1 = Account("account_1", internal_agent=deployer_agent)

    changes = [agr4bs.state.CreateAccount(account_0),
               agr4bs.state.CreateAccount(account_1),
               agr4bs.state.AddBalance("account_0", 100)]

    state.apply_batch_state_change(changes)

    payload = Payload(InternalAgentCalldata("custom_deploy_function").serialize())
    tx = agr4bs.ITransaction("account_0", "account_1", 0, payload=payload)
    vm = agr4bs.models.eth.VM()

    receipt = vm.process_tx(state.copy(), tx)

    assert receipt.reverted is False

    state.apply_batch_state_change(receipt.state_changes)

    assert state.get_account_nonce("account_0") == 1
    assert state.get_account_nonce("account_1") == 1
    assert state.get_account("account_2") is not None
    assert state.get_account_storage_at("account_2", "key") == "value"
