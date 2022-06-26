"""
    Test suite for the Environment class related to agents addition
"""

import random
import asyncio
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

    env_task = asyncio.create_task(env.run())

    await asyncio.sleep(1)

    await env.stop()
    await env_task

    for agent in agents:

        # Ensure that each agent can send to at least one other agent
        assert len(agent.context['outbound_peers']) > 0 and len(
            agent.context['outbound_peers']) <= agent.max_outbound_peers

        # Ensute that each agent can receive from at least one other agent
        assert len(agent.context['inbound_peers']) >= 0 and len(
            agent.context['inbound_peers']) <= agent.max_inbound_peers
