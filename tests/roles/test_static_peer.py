"""
    Test suite for the StatiPeer Role
"""

import agr4bs


def test_static_peer_type():
    """
    Ensures that an StaticPeer has the appropriate RoleType
    """
    role = agr4bs.roles.StaticPeer()
    assert role.type == agr4bs.RoleType.PEER


def test_static_peer_behaviors():
    """
    Ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.roles.StaticPeer()

    assert 'context_change' not in role.behaviors


def test_static_peer_addition():
    """
    Ensures that adding an StaticPeer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the StaticPeer Role
    - Agent has all the StaticPeer behaviors
    - Agent has all the StaticPeer context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.StaticPeer()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.PEER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.PEER) == role


def test_static_peer_removal():
    """
    Ensures that removing an StaticPeer Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the ORACLE Role
    - Agent has none of the StaticPeer behaviors
    - Agent has none of the StaticPeer context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.roles.StaticPeer()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.PEER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context
