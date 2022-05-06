import agr4bs
from agr4bs.Role import RoleType


def test_blockEndorserType():
    role = agr4bs.Roles.BlockEndorser()
    assert role.type == agr4bs.RoleType.BLOCK_ENDORSER


def test_blockEndorserBehaviors():
    role = agr4bs.Roles.BlockEndorser()
    assert 'endorseBlock' in role.behaviors


def test_blockEndorserAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockEndorser()
    agent.addRole(role)

    assert agent.hasRole(RoleType.BLOCK_ENDORSER)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.BLOCK_ENDORSER) == role


def test_blockEndorserRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockEndorser()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.BLOCK_ENDORSER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
