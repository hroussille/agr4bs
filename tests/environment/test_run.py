"""
    Test suite for the Environment class related to agents addition
"""

import agr4bs
import datetime


async def test_run():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    agr4bs.Factory.build_network(reset=True)
    genesis = agr4bs.Block(None, "genesis", [])

    agents = []

    for i in range(10):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, agr4bs.Factory)
        agent.add_role(agr4bs.roles.StaticPeer())
        agents.append(agent)

    env = agr4bs.Environment(agr4bs.Factory)
    env.add_role(agr4bs.roles.StaticBootstrap())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)
    scheduler = agr4bs.Scheduler(env, agr4bs.Factory, current_time=epoch)

    def condition(environment: agr4bs.Environment) -> bool:
        return environment.date < epoch + datetime.timedelta(minutes=10)

    scheduler.run(condition)
