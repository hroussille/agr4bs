import agr4bs
from agr4bs.Role import RoleType


def test_Oracle_type():
    role = agr4bs.Roles.Oracle()
    assert role.type == agr4bs.RoleType.ORACLE


def test_oracle_behaviors():
    role = agr4bs.Roles.Oracle()

    assert 'state_change' not in role.behaviors


def test_Oracle_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Oracle()
    agent.add_role(role)

    assert agent.has_role(RoleType.ORACLE)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.ORACLE) == role


def test_Oracle_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Oracle()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.ORACLE) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
