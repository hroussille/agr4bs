import agr4bs
from agr4bs.Role import RoleType


def test_groupManagerType():
    role = agr4bs.Roles.GroupManager()
    assert role.type == agr4bs.RoleType.GROUP_MANAGER


def test_blockEndorserBehaviors():
    role = agr4bs.Roles.GroupManager()
    assert 'authorize' in role.behaviors


def test_groupManagerAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.GroupManager()
    agent.addRole(role)

    assert agent.hasRole(RoleType.GROUP_MANAGER)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.GROUP_MANAGER) == role


def test_groupManagerRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.GroupManager()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.GROUP_MANAGER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
