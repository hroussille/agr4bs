"""
    Test suite for the Environment class related to agents addition
"""

import datetime
import random
from collections import Counter
import agr4bs

from agr4bs.models.eth.blockchain import Transaction, Block

def test_block_creation():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    random.seed(1)

    nb_agents = 50
    model = agr4bs.models.eth
    model.Factory.build_network(reset=True)
    genesis = Block(None, "genesis", [Transaction(
        "genesis", f"agent_{i}", 0) for i in range(nb_agents)])

    agents = []

    for i in range(nb_agents):
        agent = agr4bs.ExternalAgent(
            f"agent_{i}", genesis, model.Factory)
        agent.add_role(agr4bs.roles.StaticPeer())
        agent.add_role(model.roles.BlockchainMaintainer())
        agent.add_role(model.roles.BlockProposer())
        agent.add_role(model.roles.TransactionProposer())
        agents.append(agent)

    env = agr4bs.Environment(model.Factory)
    env.add_role(agr4bs.roles.StaticBootstrap())
    env.add_role(agr4bs.models.eth.roles.BlockCreatorElector())
    env.add_role(agr4bs.models.eth.roles.TransactionCreatorElector())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)
    scheduler = agr4bs.Scheduler(env, model.Factory, current_time=epoch)

    def condition(environment: agr4bs.Environment) -> bool:
        return environment.date < epoch + datetime.timedelta(hours=1)

    def progress(environment: agr4bs.Environment) -> bool:
        delta: datetime.timedelta = environment.date - epoch
        return min(1, delta.total_seconds() / datetime.timedelta(hours=1).total_seconds())

    scheduler.init()
    scheduler.run(condition, progress=progress)

    heads = [agent.context['blockchain'].head for agent in agents]
    heads_heights = {head.hash: head.height for head in heads}
    heads_hashes = [head.hash for head in heads]
    heads_counts = Counter(heads_hashes)

    for ref in agents:
        ref_nonce = ref.context['state'].get_account_nonce(ref.name)

        for agent in agents:
            assert agent.context['state'].get_account_nonce(
                ref.name) == ref_nonce

    # Ensure that one head is shared by all agents
    # i.e., state is consensual
    for head_hash, head_count in heads_counts.items():
        shared_percentage = 100 * head_count / len(agents)
        print("Head : " + head_hash + " shared by " + str(shared_percentage) +
              "% of the agents (height: " + str(heads_heights[head_hash]) + ")")
        assert head_count / len(agents) == 1

    for head_hash, head_height in heads_heights.items():
        assert head_height > 1
