import agr4bs
from agr4bs.Role import RoleType


def test_investeeType():
    role = agr4bs.Roles.Investee()
    assert role.type == agr4bs.RoleType.INVESTEE


def test_investeeBehaviors():
    role = agr4bs.Roles.Investee()
    assert 'receiveInvestment' in role.behaviors
    assert 'redistribute' in role.behaviors
    assert 'redistributeFull' in role.behaviors


def test_investeeAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investee()
    agent.addRole(role)

    assert agent.hasRole(RoleType.INVESTEE)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.INVESTEE) == role


def test_investeeRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investee()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.INVESTEE) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
