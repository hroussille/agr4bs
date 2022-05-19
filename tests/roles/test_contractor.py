"""
    Test suite for the Contractor Role
"""

import agr4bs


def test_contractor_type():
    """
    Ensures that a Contractor has the appropriate RoleType
    """
    role = agr4bs.roles.Contractor()
    assert role.type == agr4bs.RoleType.CONTRACTOR


def test_contractor_behaviors():
    """
    Ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.roles.Contractor()

    assert 'context_change' not in role.behaviors


def test_contractor_addition():
    """
    Ensures that adding a Contractor Role to an Agent leads
    to the appropriate behavior :

    - Agent has the CONTRACTOR Role
    - Agent has all the Contractor behaviors
    - Agent has all the Contractor context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.INTERNAL_AGENT)
    role = agr4bs.roles.Contractor()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.CONTRACTOR)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.CONTRACTOR) == role


def test_contractor_removal():
    """
    Ensures that removing a Contractor Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the CONTRACTOR Role
    - Agent has none of the Contractor behaviors
    - Agent has none of the Contractor context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.INTERNAL_AGENT)
    role = agr4bs.roles.Contractor()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.CONTRACTOR) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
