"""
    Test suite for the Environment class related to agents addition
"""

import asyncio
import agr4bs


async def test_block_creation():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Block(None, "genesis", [])

    agents = []

    for i in range(100):
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

    await asyncio.sleep(10)

    await env.stop()
    await env_task

    for agent in agents:
        print(agent.name + " Blockchain height : " +
              str(agent.context['blockchain'].head.height))
        print(agent.context['state'].get_account_balance("agent_1"))
