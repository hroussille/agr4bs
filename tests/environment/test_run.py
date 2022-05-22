"""
    Test suite for the Environment class related to agents addition
"""

import asyncio
import agr4bs


async def test_run():
    """
        Test that the environment can be run and stopped later
    """
    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Block(None, "genesis", [])

    agents = []

    for i in range(2000):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis)
        agent.add_role(agr4bs.roles.Peer())
        agents.append(agent)

    env = agr4bs.Environment()

    for agent in agents:
        env.add_agent(agent)

    env_task = asyncio.create_task(env.run())
    await env.stop()
    await asyncio.gather(env_task)
