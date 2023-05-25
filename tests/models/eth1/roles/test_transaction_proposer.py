"""
    Test suite for the TransactionProposer Role
"""

import agr4bs

from agr4bs.models.eth1.blockchain import Block, Transaction


def test_transaction_proposer_type():
    """
    Ensures that a TransactionProposer has the appropriate RoleType
    """
    role = agr4bs.models.eth1.roles.TransactionProposer()
    assert role.type == agr4bs.RoleType.TRANSACTION_PROPOSER


def test_transaction_proposer_behaviors():
    """
    Ensures that a TransactionProposer has the appropriate behaviors :

    - create_transaction
    - proposer_transaction

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth1.roles.TransactionProposer()

    assert 'create_transaction' in role.behaviors
    assert 'propose_transaction' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_transaction_proposer_addition():
    """
    Ensures that adding a TransactionProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the TRANSACTION_PROPOSER Role
    - Agent has all the TransactionProposer behaviors
    - Agent has all the TransactionProposer context changes
    """
    genesis = Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth1.Factory)
    role = agr4bs.models.eth1.roles.TransactionProposer()
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth1.roles.BlockchainMaintainer())
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.TRANSACTION_PROPOSER) == role


def test_transaction_proposer_removal():
    """
    Ensures that removing a TransactionProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the TRANSACTION_PROPOSER Role
    - Agent has none of the TransactionProposer behaviors
    - Agent has none of the TransactionProposer context changes
    """
    genesis = Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth1.Factory)
    role = agr4bs.models.eth1.roles.TransactionProposer()
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth1.roles.BlockchainMaintainer())
    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.TRANSACTION_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
