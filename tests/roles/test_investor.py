"""
    Test suite for the Investor Role
"""

import agr4bs


def test_investor_type():
    """
    Ensures that an Investor has the appropriate RoleType
    """
    role = agr4bs.roles.Investor()
    assert role.type == agr4bs.RoleType.INVESTOR


def test_investor_behaviors():
    """
    Ensures that an Investor has the appropriate behaviors :

    - specify_investment
    - invest
    - withdraw

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.roles.Investor()

    assert 'specify_investment' in role.behaviors
    assert 'invest' in role.behaviors
    assert 'withdraw' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_investor_addition():
    """
    Ensures that adding an Investor Role to an Agent leads
    to the appropriate behavior :

    - Agent has the Investor Role
    - Agent has all the Investor behaviors
    - Agent has all the Investor context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.Investor()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.INVESTOR)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.INVESTOR) == role


def test_investor_removal():
    """
    Ensures that removing a Investor Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the INVESTOR Role
    - Agent has none of the Investor behaviors
    - Agent has none of the Investor context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.Investor()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.INVESTOR) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
