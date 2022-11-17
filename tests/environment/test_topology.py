"""
    Test suite for the Environment class related to agents addition
"""

import datetime
import random
import agr4bs
from agr4bs.agents.external_agent import ExternalAgent


async def test_block_creation():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    random.seed(1)

    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Block(None, "genesis", [])

    agents: ExternalAgent = []

    for i in range(20):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, agr4bs.Factory)
        agent.add_role(agr4bs.roles.Peer())
        agents.append(agent)

    env = agr4bs.Environment(agr4bs.Factory)
    env.add_role(agr4bs.roles.Bootstrap())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)
    
    scheduler = agr4bs.Scheduler(env, agr4bs.Factory, current_time=epoch)

    def condition(environment: agr4bs.Environment) -> bool:
        return environment.date < epoch + datetime.timedelta(days=1)

    def progress(environment: agr4bs.Environment) -> bool:
        delta: datetime.timedelta = environment.date - epoch
        return min(1, delta.total_seconds() / datetime.timedelta(days=1).total_seconds())

    scheduler.init()
    scheduler.run(condition, progress=progress)

    for agent in agents:
        # Ensure that each agent can send to max_outbound_peers other agents
        assert len(agent.context['outbound_peers']) == agent.max_outbound_peers

        # Ensute that each agent can receive from at least max_outbound_peers other agents
        assert len(agent.context['inbound_peers']) >= agent.max_outbound_peers

