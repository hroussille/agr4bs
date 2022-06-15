"""
    Test suite for the Environment class related to agents addition
"""

import random
import asyncio
from collections import Counter
import agr4bs


async def test_block_creation():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    random.seed(1)

    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Block(None, "genesis", [])

    agents = []

    for i in range(50):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis)
        agent.add_role(agr4bs.roles.StaticPeer())
        agent.add_role(agr4bs.roles.BlockchainMaintainer())
        agent.add_role(agr4bs.roles.BlockProposer())
        agents.append(agent)

    env = agr4bs.Environment()
    env.add_role(agr4bs.roles.StaticBootstrap())
    env.add_role(agr4bs.roles.BlockCreatorElector())

    for agent in agents:
        env.add_agent(agent)

    env_task = asyncio.create_task(env.run())

    await asyncio.sleep(5)

    env.remove_role(agr4bs.roles.BlockCreatorElector())

    await asyncio.sleep(1)

    await env.stop()
    await env_task

    heads = [agent.context['blockchain'].head for agent in agents]
    head_hashes = [head.hash for head in heads]
    head_counts = Counter(head_hashes)

    # Ensure that one head is shared by all agents
    # i.e., state is consensual
    for _, head_count in head_counts.items():
        assert head_count / len(agents) == 1
