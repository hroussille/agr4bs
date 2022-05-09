import agr4bs
from agr4bs.Role import RoleType


def test_TransactionProposer_type():
    role = agr4bs.Roles.TransactionProposer()
    assert role.type == agr4bs.RoleType.TRANSACTION_PROPOSER


def test_TransactionProposer_behaviors():
    role = agr4bs.Roles.TransactionProposer()

    assert 'create_transaction' in role.behaviors
    assert 'propose_transaction' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_TransactionProposer_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionProposer()
    agent.add_role(role)

    assert agent.has_role(RoleType.TRANSACTION_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.TRANSACTION_PROPOSER) == role


def test_TransactionProposer_removal():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.TransactionProposer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.TRANSACTION_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
