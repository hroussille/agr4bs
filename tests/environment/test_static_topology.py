"""
    Test suite for the Environment class related to agents addition
"""

import random
import asyncio
import numpy as np
from collections import Counter
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

    for i in range(1000):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis)
        agent.add_role(agr4bs.roles.StaticPeer())
        agents.append(agent)

    env = agr4bs.Environment()
    env.add_role(agr4bs.roles.StaticBootstrap())

    for agent in agents:
        env.add_agent(agent)

    env_task = asyncio.create_task(env.run())

    await asyncio.sleep(20)

    await env.stop()
    await env_task

    for agent in agents:
        # Ensure that each agent can send to max_outbound_peers other agents
        assert len(agent.context['outbound_peers']) == agent.max_outbound_peers

        # Ensute that each agent can receive from at least max_outbound_peers other agents
        assert len(agent.context['inbound_peers']) >= agent.max_outbound_peers
