import agr4bs
from agr4bs.Role import RoleType


def test_Investee_type():
    role = agr4bs.Roles.Investee()
    assert role.type == agr4bs.RoleType.INVESTEE


def test_Investee_behaviors():
    role = agr4bs.Roles.Investee()

    assert 'receive_investment' in role.behaviors
    assert 'redistribute' in role.behaviors
    assert 'redistribute_full' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_Investee_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investee()
    agent.add_role(role)

    assert agent.has_role(RoleType.INVESTEE)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.INVESTEE) == role


def test_Investee_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investee()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.INVESTEE) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
