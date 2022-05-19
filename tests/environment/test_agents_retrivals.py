"""
    Test suite for the Environment class related to agents addition
"""

import agr4bs


def test_agent_retrieval():
    """
        Test that an agent can be retrived by its object reference
    """
    agent0 = agr4bs.Agent("agent0", agr4bs.AgentType.EXTERNAL_AGENT)
    agent1 = agr4bs.Agent("agent1", agr4bs.AgentType.EXTERNAL_AGENT)
    agent2 = agr4bs.Agent("agent2", agr4bs.AgentType.EXTERNAL_AGENT)
    agent3 = agr4bs.Agent("agent3", agr4bs.AgentType.EXTERNAL_AGENT)

    env = agr4bs.Environment()
    env.add_agent(agent0)
    env.add_agent(agent1)
    env.add_agent(agent2)

    assert env.has_agent(agent0)
    assert env.has_agent(agent1)
    assert env.has_agent(agent2)
    assert not env.has_agent(agent3)

    assert env.get_agent(agent0) == agent0
    assert env.get_agent(agent1) == agent1
    assert env.get_agent(agent2) == agent2
    assert env.get_agent(agent3) is None


def test_agent_retrieval_by_name():
    """
        Test that an agent can be retrived by its name
    """
    agent0 = agr4bs.Agent("agent0", agr4bs.AgentType.EXTERNAL_AGENT)
    agent1 = agr4bs.Agent("agent1", agr4bs.AgentType.EXTERNAL_AGENT)
    agent2 = agr4bs.Agent("agent2", agr4bs.AgentType.EXTERNAL_AGENT)
    agent3 = agr4bs.Agent("agent3", agr4bs.AgentType.EXTERNAL_AGENT)

    env = agr4bs.Environment()
    env.add_agent(agent0)
    env.add_agent(agent1)
    env.add_agent(agent2)

    assert env.has_agent(agent0)
    assert env.has_agent(agent1)
    assert env.has_agent(agent2)
    assert not env.has_agent(agent3)

    assert env.get_agent_by_name(agent0.name) == agent0
    assert env.get_agent_by_name(agent1.name) == agent1
    assert env.get_agent_by_name(agent2.name) == agent2
    assert env.get_agent_by_name(agent3.name) is None
