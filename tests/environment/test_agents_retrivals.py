"""
    Test suite for the Environment class related to agents addition
"""

import agr4bs


def test_agent_retrieval():
    """
        Test that an agent can be retrived by its object reference
    """
    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Factory.build_block(None, "genesis", [])

    agent0 = agr4bs.ExternalAgent("agent0", genesis, agr4bs.Factory)
    agent1 = agr4bs.ExternalAgent("agent1", genesis, agr4bs.Factory)
    agent2 = agr4bs.ExternalAgent("agent2", genesis, agr4bs.Factory)
    agent3 = agr4bs.ExternalAgent("agent3", genesis, agr4bs.Factory)

    env = agr4bs.Environment(agr4bs.Factory)
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
    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Factory.build_block(None, "genesis", [])

    agent0 = agr4bs.ExternalAgent("agent0", genesis, agr4bs.Factory)
    agent1 = agr4bs.ExternalAgent("agent1", genesis, agr4bs.Factory)
    agent2 = agr4bs.ExternalAgent("agent2", genesis, agr4bs.Factory)
    agent3 = agr4bs.ExternalAgent("agent3", genesis, agr4bs.Factory)

    env = agr4bs.Environment(agr4bs.Factory)
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
