"""
    Test suite for the TransactionEndorser Role
"""

import agr4bs


def test_transaction_endorser_type():
    """
    Ensures that a TransactionEndorser has the appropriate RoleType
    """
    role = agr4bs.models.eth.roles.TransactionEndorser()
    assert role.type == agr4bs.RoleType.TRANSACTION_ENDORSER


def test_transaction_endorser_behaviors():
    """
    Ensures that a TransactionEndorser has the appropriate behaviors :

    - endorse_transaction

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth.roles.TransactionEndorser()

    assert 'endorse_transaction' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_transaction_endorser_addition():
    """
    Ensures that adding a TransactionEndorser Role to an Agent leads
    to the appropriate behavior :

    - Agent has the TRANSACTION_ENDORSER Role
    - Agent has all the TransactionEndorser behaviors
    - Agent has all the TransactionEndorser context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth.roles.TransactionEndorser()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_ENDORSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.TRANSACTION_ENDORSER) == role


def test_transaction_endorser_removal():
    """
    Ensures that removing a TransactionEndorser Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the TRANSACTION_ENDORSER Role
    - Agent has none of the TransactionEndorser behaviors
    - Agent has none of the TransactionEndorser context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth.roles.TransactionEndorser()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_ENDORSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
