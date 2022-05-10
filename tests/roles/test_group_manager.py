"""
    Test suite for the GroupManager Role
"""

import agr4bs


def test_group_manager_type():
    """
    Ensures that a GroupMamager has the appropriate RoleType
    """
    role = agr4bs.roles.GroupManager()
    assert role.type == agr4bs.RoleType.GROUP_MANAGER


def test_group_manager_behaviors():
    """
    Ensures that an Investee has the appropriate behaviors :

    - authorize

    Also ensures that the `state_change` static method is NOT exported.
    """
    role = agr4bs.roles.GroupManager()

    assert 'authorize' in role.behaviors
    assert 'state_change' not in role.behaviors


def test_group_manager_addition():
    """
    Ensures that adding a GroupManager Role to an Agent leads
    to the appropriate behavior :

    - Agent has the GROUP_MANAGER Role
    - Agent has all the GroupManager behaviors
    - Agent has all the GroupManager state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.GroupManager()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.GROUP_MANAGER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(agr4bs.RoleType.GROUP_MANAGER) == role


def test_group_manager_removal():
    """
    Ensures that removing a GroupManager Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the GROUP_MANAGER Role
    - Agent has none of the GroupManager behaviors
    - Agent has none of the GroupManager state changes
    """
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.roles.GroupManager()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.GROUP_MANAGER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
