"""
    Test suite for the Investee Role
"""

import agr4bs


def test_investee_type():
    """
    Ensures that an Investee has the appropriate RoleType
    """
    role = agr4bs.models.eth.roles.Investee()
    assert role.type == agr4bs.RoleType.INVESTEE


def test_investee_behaviors():
    """
    Ensures that an Investee has the appropriate behaviors :

    - receive_investment
    - redistribute
    - redistribute_full

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth.roles.Investee()

    assert 'receive_investment' in role.behaviors
    assert 'redistribute' in role.behaviors
    assert 'redistribute_full' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_investee_addition():
    """
    Ensures that adding an Investee Role to an Agent leads
    to the appropriate behavior :

    - Agent has the Investee Role
    - Agent has all the Investee behaviors
    - Agent has all the Investee context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth.roles.Investee()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.INVESTEE)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.INVESTEE) == role


def test_investee_removal():
    """
    Ensures that removing a Investee Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the INVESTEE Role
    - Agent has none of the Investee behaviors
    - Agent has none of the Investee context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth.roles.Investee()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.INVESTEE) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
