import agr4bs
from agr4bs.Role import RoleType


def test_BlockchainMaintainer_type():
    role = agr4bs.Roles.BlockchainMaintainer()
    assert role.type == agr4bs.RoleType.BLOCKCHAIN_MAINTAINER


def test_BlockchainMaintainer_behaviors():
    role = agr4bs.Roles.BlockchainMaintainer()

    assert 'append_block' in role.behaviors
    assert 'execute_transaction' in role.behaviors
    assert 'validate_block' in role.behaviors
    assert 'validate_transaction' in role.behaviors
    assert 'store_transaction' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_BlockchainMaintainer_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockchainMaintainer()
    agent.add_role(role)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.BLOCKCHAIN_MAINTAINER) == role


def test_BlockchainMaintainer_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockchainMaintainer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.BLOCKCHAIN_MAINTAINER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
