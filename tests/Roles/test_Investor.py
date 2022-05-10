import agr4bs
from agr4bs.Role import RoleType


def test_Investor_type():
    role = agr4bs.Roles.Investor()
    assert role.type == agr4bs.RoleType.INVESTOR


def test_Investor_behaviors():
    role = agr4bs.Roles.Investor()

    assert 'specify_investment' in role.behaviors
    assert 'invest' in role.behaviors
    assert 'withdraw' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_Investor_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investor()
    agent.add_role(role)

    assert agent.has_role(RoleType.INVESTOR)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.INVESTOR) == role


def test_Investor_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investor()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.INVESTOR) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
