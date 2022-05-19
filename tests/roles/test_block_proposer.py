"""
    Test suite for the BlockProposer Role
"""

import agr4bs


def test_block_proposer_type():
    """
    Ensures that a BlockProposer has the appropriate RoleType
    """
    role = agr4bs.roles.BlockProposer()
    assert role.type == agr4bs.RoleType.BLOCK_PROPOSER


def test_block_proposer_behaviors():
    """
    Ensures that a BlockProposer has the appropriate behaviors :

    - select_transaction
    - create_block
    - propose_block

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.roles.BlockProposer()

    assert 'select_transaction' in role.behaviors
    assert 'create_block' in role.behaviors
    assert 'propose_block' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_block_proposer_addition():
    """
    Ensures that adding a BlockProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCK_PROPOSER Role
    - Agent has all the BlockProposer behaviors
    - Agent has all the BlockProposer context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.BlockProposer()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BLOCK_PROPOSER) == role


def test_block_proposer_removal():
    """
    Ensures that removing a BlockProposer Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCK_PROPOSER Role
    - Agent has none of the BlockProposer behaviors
    - Agent has none of the BlockProposer context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.BlockProposer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
