"""
    Test suite for the Environment class related to agents addition
"""

import agr4bs
import datetime

from agr4bs.models.eth2.blockchain import Transaction, Block
from agr4bs.models.eth2.factory import Factory

def test_run():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    Factory.build_network(reset=True)
    genesis = Block(None, "genesis", [])

    agents = []

    for i in range(10):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, Factory)
        agent.add_role(agr4bs.roles.StaticPeer())
        agents.append(agent)

    env = agr4bs.Environment(Factory)
    env.add_role(agr4bs.roles.StaticBootstrap())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)
    scheduler = agr4bs.Scheduler(env, Factory, current_time=epoch)
    scheduler.init()

    def condition(environment: agr4bs.Environment) -> bool:
        return environment.date < epoch + datetime.timedelta(seconds=12*32)

    scheduler.run(condition)
