import agr4bs
from agr4bs.Role import RoleType


def test_transactionEndorserType():
    role = agr4bs.Roles.TransactionEndorser()
    assert role.type == agr4bs.RoleType.TRANSACTION_ENDORSER


def test_transactionEndorserBehaviors():
    role = agr4bs.Roles.TransactionEndorser()
    assert 'endorseTransaction' in role.behaviors


def test_transactionEndorserAddition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionEndorser()
    agent.addRole(role)

    assert agent.hasRole(RoleType.TRANSACTION_ENDORSER)

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior)

    for stateChange in role.stateChange().mount():
        assert stateChange in agent.state

    assert agent.getRole(RoleType.TRANSACTION_ENDORSER) == role


def test_blockEndorserRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionEndorser()

    agent.addRole(role)
    agent.removeRole(role)

    assert agent.hasRole(RoleType.TRANSACTION_ENDORSER) == False

    for behavior in role.behaviors:
        assert agent.hasBehavior(behavior) == False

    for stateChange in role.stateChange().mount():
        assert stateChange not in agent.state
