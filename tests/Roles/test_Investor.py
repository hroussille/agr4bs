import agr4bs
from agr4bs.Role import RoleType


def test_investorType():
    role = agr4bs.Roles.Investor()
    assert role.type == agr4bs.RoleType.INVESTOR


def test_investorBehaviors():
    role = agr4bs.Roles.Investor()
    assert 'specifyInvestment' in role.behaviors
    assert 'invest' in role.behaviors
    assert 'withdraw' in role.behaviors


def test_investorAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investor()
    agent.addRole(role)

    assert agent.hasRole(RoleType.INVESTOR)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.INVESTOR) == role


def test_investorRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Investor()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.INVESTOR) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
