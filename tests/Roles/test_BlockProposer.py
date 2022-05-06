import agr4bs
from agr4bs.Role import RoleType


def test_blockProposerType():
    role = agr4bs.Roles.BlockProposer()
    assert role.type == agr4bs.RoleType.BLOCK_PROPOSER


def test_blockProposerBehaviors():
    role = agr4bs.Roles.BlockProposer()

    assert 'selectTransaction' in role.behaviors
    assert 'createBlock' in role.behaviors
    assert 'proposeBlock' in role.behaviors


def test_blockProposerAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockProposer()
    agent.addRole(role)

    assert agent.hasRole(RoleType.BLOCK_PROPOSER)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.BLOCK_PROPOSER) == role


def test_blockProposerRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.BlockProposer()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.BLOCK_PROPOSER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
