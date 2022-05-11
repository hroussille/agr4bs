"""
    Test suite for the Environment class related to agents deletion
"""

import pytest
import agr4bs


def test_agent_deletion():
    """
        Test that an agent is correctly removed from the Environment
    """

    agent = agr4bs.Agent("agent0")
    env = agr4bs.Environment()

    env.add_agent(agent)
    env.remove_agent(agent)

    # pylint: disable=protected-access
    assert agent.name not in env._agents


def test_agent_double_deletion():
    """
        Test that an agent cannot be deleted twice from the Environment
    """

    agent = agr4bs.Agent("agent0")
    env = agr4bs.Environment()

    env.add_agent(agent)
    env.remove_agent(agent)

    with pytest.raises(ValueError) as excinfo:
        env.remove_agent(agent)

    assert "Attempting to remove a non existing agent from the environment" in str(
        excinfo.value)


def test_agent_retrieval():
    """
        Test that an agent can be retrived by its object reference
    """


def test_agent_retrieval_by_name():
    """
        Test that an agent can be retrived by its name
    """
