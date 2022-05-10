"""
    Test suite for the BlockEndorser Role
"""

import agr4bs


def test_block_endorser_type():
    """
    Ensures that a BlockEndorser has the appropriate RoleType
    """
    role = agr4bs.roles.BlockEndorser()
    assert role.type == agr4bs.RoleType.BLOCK_ENDORSER


def test_block_endorser_behaviors():
    """
    Ensures that a BlockEndorser has the appropriate behaviors :

    - endorse_block

    Also ensures that the `state_change` static method is NOT exported.
    """
    role = agr4bs.roles.BlockEndorser()

    assert 'endorse_block' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_block_endorser_addition():
    """
    Ensures that adding a BlockEndorser Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCK_ENDORSER Role
    - Agent has all the BlockEndorser behaviors
    - Agent has all the BlockEndorser state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.BlockEndorser()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_ENDORSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(agr4bs.RoleType.BLOCK_ENDORSER) == role


def test_block_endorser_removal():
    """
    Ensures that removing a BlockEndorser Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCK_ENDORSER Role
    - Agent has none of the BlockEndorser behaviors
    - Agent has none of the BlockEndorser state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.BlockEndorser()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_ENDORSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
