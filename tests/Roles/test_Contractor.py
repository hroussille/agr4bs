import agr4bs
from agr4bs.Role import RoleType


def test_Contractor_type():
    role = agr4bs.Roles.Contractor()
    assert role.type == agr4bs.RoleType.CONTRACTOR


def test_Contractor_behaviors():
    role = agr4bs.Roles.Contractor()

    assert 'state_change' not in role.behaviors


def test_Contractor_addition():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Contractor()
    agent.add_role(role)

    assert agent.has_role(RoleType.CONTRACTOR)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for state_change in role.state_change().mount():
        assert state_change in agent.state

    assert agent.get_role(RoleType.CONTRACTOR) == role


def test_ContractorRemoval():
    agent = agr4bs.Agent("agent_0")
    role = agr4bs.Roles.Contractor()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(RoleType.CONTRACTOR) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for state_change in role.state_change().mount():
        assert state_change not in agent.state
