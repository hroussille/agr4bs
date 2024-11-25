"""
    Test suite for the Bootstrap Role
"""

import agr4bs


def test_bootstrap_type():
    """
    Ensures that an Bootstrap has the appropriate RoleType
    """
    role = agr4bs.roles.Bootstrap()
    assert role.type == agr4bs.RoleType.BOOTSTRAP


def test_bootstrap_behaviors():
    """
    Ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.roles.Bootstrap()

    assert 'context_change' not in role.behaviors


def test_bootstrap_addition():
    """
    Ensures that adding an Bootstrap Role to an Agent leads
    to the appropriate behavior :

    - Agent has the Bootstrap Role
    - Agent has all the Bootstrap behaviors
    - Agent has all the Bootstrap context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.Bootstrap()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BOOTSTRAP)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BOOTSTRAP) == role


def test_bootstrap_removal():
    """
    Ensures that removing an Bootstrap Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the ORACLE Role
    - Agent has none of the Bootstrap behaviors
    - Agent has none of the Bootstrap context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.Bootstrap()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BOOTSTRAP) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
