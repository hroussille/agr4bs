import agr4bs
from agr4bs.Role import RoleType


def test_oracleType():
    role = agr4bs.Roles.Oracle()
    assert role.type == agr4bs.RoleType.ORACLE


def test_oracleAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Oracle()
    agent.addRole(role)

    assert agent.hasRole(RoleType.ORACLE)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.ORACLE) == role


def test_oracleRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Oracle()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.ORACLE) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
