"""
    Test suite for the Environment class related to agents addition
"""

import random
import asyncio
import numpy as np
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
        agent.add_role(agr4bs.roles.Peer())
        agent.add_role(agr4bs.roles.BlockchainMaintainer())
        agent.add_role(agr4bs.roles.BlockProposer())
        agents.append(agent)

    env = agr4bs.Environment()
    env.add_role(agr4bs.roles.Bootstrap())
    env.add_role(agr4bs.roles.BlockCreatorElector())

    for agent in agents:
        env.add_agent(agent)

    env_task = asyncio.create_task(env.run())

    await asyncio.sleep(5)

    env.remove_role(agr4bs.roles.BlockCreatorElector())

    await asyncio.sleep(1)

    await env.stop()
    await env_task

    # heights = np.array(
    #    [agent.context['blockchain'].head.height for agent in agents])
    #avg_height = np.average(heights)
    #std_height = np.std(heights)

    head_hashes = [agent.context['blockchain'].head.hash for agent in agents]
    head_counts = Counter(head_hashes)

    # Ensure that one head is shared by all agents
    # i.e., state is consensual
    for _, head_count in head_counts.items():
        assert head_count / len(agents) == 1

    #print("Average blockchain height : " + str(avg_height))
    #print("Std dev height : " + str(std_height))

    # for head_hash, head_count in head_counts.items():
    #    print("Head : " + head_hash + " : " +
    #          str(100 * head_count / len(agents)) + " % ")
