import agr4bs
from agr4bs.Role import RoleType


def test_GroupManager_type():
    role = agr4bs.Roles.GroupManager()
    assert role.type == agr4bs.RoleType.GROUP_MANAGER


def test_GroupManager_behaviors():
    role = agr4bs.Roles.GroupManager()

    assert 'authorize' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_GroupManager_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.GroupManager()
    agent.add_role(role)

    assert agent.has_role(RoleType.GROUP_MANAGER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.GROUP_MANAGER) == role


def test_GroupManager_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.GroupManager()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.GROUP_MANAGER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
