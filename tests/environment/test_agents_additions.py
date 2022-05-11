"""
    Test suite for the Environment class related to agents addition
"""

import pytest
import agr4bs


def test_agent_addition():
    """
        Test that an agent is correctly added to the Environment
    """
    agent = agr4bs.Agent("agent0")
    env = agr4bs.Environment()

    env.add_agent(agent)

    # pylint: disable=protected-access
    assert agent.name in env._agents

    # pylint: disable=protected-access
    assert env._agents[agent.name] == agent


def test_agent_double_addition():
    """
        Test that an agent cannot be added twice
    """

    agent = agr4bs.Agent("agent0")
    env = agr4bs.Environment()

    env.add_agent(agent)

    with pytest.raises(ValueError) as excinfo:
        env.add_agent(agent)

    assert "Attempting to add an already existing agent from the environment" in str(
        excinfo.value)


def test_agent_double_addition_name_conflict():
    """
        Test that two agent with conflicting mames cannot be
        added to the state
    """
    agent0 = agr4bs.Agent("agent0")
    agent1 = agr4bs.Agent("agent0")

    env = agr4bs.Environment()

    env.add_agent(agent0)

    with pytest.raises(ValueError) as excinfo:
        env.add_agent(agent1)

    assert "Attempting to add an already existing agent from the environment" in str(
        excinfo.value)
