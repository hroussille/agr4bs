"""
    Test suite for the Oracle Role
"""

import agr4bs


def test_oracle_type():
    """
    Ensures that an Oracle has the appropriate RoleType
    """
    role = agr4bs.models.eth2.roles.Oracle()
    assert role.type == agr4bs.RoleType.ORACLE


def test_oracle_behaviors():
    """
    Ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth2.roles.Oracle()

    assert 'context_change' not in role.behaviors


def test_oracle_addition():
    """
    Ensures that adding an Oracle Role to an Agent leads
    to the appropriate behavior :

    - Agent has the Oracle Role
    - Agent has all the Oracle behaviors
    - Agent has all the Oracle context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth2.roles.Oracle()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.ORACLE)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.ORACLE) == role


def test_oracle_removal():
    """
    Ensures that removing an Oracle Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the ORACLE Role
    - Agent has none of the Oracle behaviors
    - Agent has none of the Oracle context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth2.roles.Oracle()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.ORACLE) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
