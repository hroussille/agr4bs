import agr4bs
from agr4bs.Role import RoleType


def test_BlockProposer_type():
    role = agr4bs.Roles.BlockProposer()
    assert role.type == agr4bs.RoleType.BLOCK_PROPOSER


def test_BlockProposer_behaviors():
    role = agr4bs.Roles.BlockProposer()

    assert 'select_transaction' in role.behaviors
    assert 'create_block' in role.behaviors
    assert 'propose_block' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_BlockProposer_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockProposer()
    agent.add_role(role)

    assert agent.has_role(RoleType.BLOCK_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.BLOCK_PROPOSER) == role


def test_BlockProposer_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockProposer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.BLOCK_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
