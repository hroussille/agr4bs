import agr4bs
from agr4bs.Role import RoleType


def test_contractorType():
    role = agr4bs.Roles.Contractor()
    assert role.type == agr4bs.RoleType.CONTRACTOR


def test_contractorAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Contractor()
    agent.addRole(role)

    assert agent.hasRole(RoleType.CONTRACTOR)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.CONTRACTOR) == role


def test_contractorRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Contractor()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.CONTRACTOR) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
