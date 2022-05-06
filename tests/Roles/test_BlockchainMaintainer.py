import agr4bs
from agr4bs.Role import RoleType


def test_blockchainMaintainerType():
    role = agr4bs.Roles.BlockchainMaintainer()
    assert role.type == agr4bs.RoleType.BLOCKCHAIN_MAINTAINER


def test_blockchainMaintainerBehaviors():
    role = agr4bs.Roles.BlockchainMaintainer()

    assert 'appendBlock' in role.behaviors
    assert 'executeTransaction' in role.behaviors
    assert 'validateBlock' in role.behaviors
    assert 'validateTransaction' in role.behaviors
    assert 'storeTransaction' in role.behaviors


def test_blockchainMaintainerAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockchainMaintainer()
    agent.addRole(role)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.BLOCKCHAIN_MAINTAINER) == role


def test_blockchainMaintainerRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockchainMaintainer()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.BLOCKCHAIN_MAINTAINER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
