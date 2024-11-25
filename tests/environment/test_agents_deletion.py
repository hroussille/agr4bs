"""
    Test suite for the Environment class related to agents deletion
"""

import pytest
import agr4bs


def test_agent_deletion():
    """
        Test that an agent is correctly removed from the Environment
    """

    agr4bs.IFactory.build_network(reset=True)
    genesis = agr4bs.IFactory.build_block(None, "genesis", [])
    agent = agr4bs.ExternalAgent("agent0", genesis, agr4bs.IFactory)
    env = agr4bs.Environment(agr4bs.IFactory)

    env.add_agent(agent)
    env.remove_agent(agent)

    # pylint: disable=protected-access
    assert agent.name not in env._agents


def test_agent_double_deletion():
    """
        Test that an agent cannot be deleted twice from the Environment
    """

    agr4bs.IFactory.build_network(reset=True)
    genesis = agr4bs.IFactory.build_block(None, "genesis", [])
    agent = agr4bs.ExternalAgent("agent0", genesis, agr4bs.IFactory)
    env = agr4bs.Environment(agr4bs.IFactory)

    env.add_agent(agent)
    env.remove_agent(agent)

    with pytest.raises(ValueError) as excinfo:
        env.remove_agent(agent)

    assert "Attempting to remove a non existing agent from the environment" in str(
        excinfo.value)
