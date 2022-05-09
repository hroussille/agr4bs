import agr4bs
from agr4bs.Role import RoleType


def test_BlockEndorser_Type():
    role = agr4bs.Roles.BlockEndorser()
    assert role.type == agr4bs.RoleType.BLOCK_ENDORSER


def test_BlockEndorser_behaviors():
    role = agr4bs.Roles.BlockEndorser()

    assert 'endorse_block' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_BlockEndorser_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockEndorser()
    agent.add_role(role)

    assert agent.has_role(RoleType.BLOCK_ENDORSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.BLOCK_ENDORSER) == role


def test_BlockEndorser_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockEndorser()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.BLOCK_ENDORSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
