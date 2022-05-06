import agr4bs
from agr4bs.Role import RoleType


def test_transactionProposerType():
    role = agr4bs.Roles.TransactionProposer()
    assert role.type == agr4bs.RoleType.TRANSACTION_PROPOSER


def test_transactionProposerBehaviors():
    role = agr4bs.Roles.TransactionProposer()

    assert 'createTransaction' in role.behaviors
    assert 'proposeTransaction' in role.behaviors


def test_transactionProposerAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionProposer()
    agent.addRole(role)

    assert agent.hasRole(RoleType.TRANSACTION_PROPOSER)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.TRANSACTION_PROPOSER) == role


def test_transactionProposerRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionProposer()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.TRANSACTION_PROPOSER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
