"""
    Test suite for the Environment class related to agents addition
"""

import datetime
import random
import agr4bs
from agr4bs.agents.external_agent import ExternalAgent


def test_static_topology():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    random.seed(1)

    agr4bs.IFactory.build_network(reset=True)
    genesis = agr4bs.IBlock(None, "genesis", [])

    agents: ExternalAgent = []

    for i in range(10):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, agr4bs.IFactory)
        agent.add_role(agr4bs.roles.StaticPeer())
        agents.append(agent)

    env = agr4bs.Environment(agr4bs.IFactory)
    env.add_role(agr4bs.roles.StaticBootstrap())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)

    scheduler = agr4bs.Scheduler(env, agr4bs.IFactory, current_time=epoch)

    def condition(environment: agr4bs.Environment):
        return environment.date < epoch + datetime.timedelta(minutes=5)

    scheduler.init()
    scheduler.run(condition)

    for agent in agents:
        # Ensure that each agent can send to at least one other agent
        assert len(agent.context['outbound_peers']) >= 1

        # Ensute that each agent can receive from at least one other agent
        assert len(agent.context['inbound_peers']) >= 1
