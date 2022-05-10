"""
    Test suite for the TransactionProposer Role
"""

import agr4bs


def test_transaction_proposer_type():
    """
    Ensures that a TransactionProposer has the appropriate RoleType
    """
    role = agr4bs.roles.TransactionProposer()
    assert role.type == agr4bs.RoleType.TRANSACTION_PROPOSER


def test_transaction_proposer_behaviors():
    """
    Ensures that a TransactionProposer has the appropriate behaviors :

    - create_transaction
    - proposer_transaction

    Also ensures that the `state_change` static method is NOT exported.
    """
    role = agr4bs.roles.TransactionProposer()

    assert 'create_transaction' in role.behaviors
    assert 'propose_transaction' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_transaction_proposer_addition():
    """
    Ensures that adding a TransactionProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the TRANSACTION_PROPOSER Role
    - Agent has all the TransactionProposer behaviors
    - Agent has all the TransactionProposer state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.TransactionProposer()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(agr4bs.RoleType.TRANSACTION_PROPOSER) == role


def test_transaction_proposer_removal():
    """
    Ensures that removing a TransactionProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the TRANSACTION_PROPOSER Role
    - Agent has none of the TransactionProposer behaviors
    - Agent has none of the TransactionProposer state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.TransactionProposer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
