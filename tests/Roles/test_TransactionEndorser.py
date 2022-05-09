import agr4bs
from agr4bs.Role import RoleType


def test_TransactionEndorser_type():
    role = agr4bs.Roles.TransactionEndorser()
    assert role.type == agr4bs.RoleType.TRANSACTION_ENDORSER


def test_TransactionEndorser_behaviors():
    role = agr4bs.Roles.TransactionEndorser()

    assert 'endorse_transaction' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_TransactionEndorser_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionEndorser()
    agent.add_role(role)

    assert agent.has_role(RoleType.TRANSACTION_ENDORSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.TRANSACTION_ENDORSER) == role


def test_TransactionEndorser_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionEndorser()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.TRANSACTION_ENDORSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
