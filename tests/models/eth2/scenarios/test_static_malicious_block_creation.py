"""
    Test suite for the Environment class related to agents addition
"""

import datetime
import random
from collections import Counter
import agr4bs

from agr4bs.models.eth2.blockchain import Transaction, Block

N_BLOCKS = 32
JITTER = 12
TIME = N_BLOCKS * 12 + JITTER

def test_block_creation():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """
    random.seed(random.randint(0, 1000))

    nb_agents = 32
    model = agr4bs.models.eth2
    model.RLFactory.build_network(reset=True)

    account_transactions = [Transaction("genesis", f"agent_{i}", i, 0, 32 * 10 ** 18) for i in range(nb_agents)]
    deposit_transactions = [Transaction(f"agent_{i}", "deposit_contract", 0, 0, 32 * 10 ** 18) for i in range(nb_agents)]

    genesis = Block(None, "genesis", 0, account_transactions + deposit_transactions)
    
    agents = []

    for i in range(nb_agents):
        agent = agr4bs.ExternalAgent(
            f"agent_{i}", genesis, model.RLFactory)
        agent.add_role(agr4bs.roles.StaticPeer())
        agent.add_role(model.roles.BlockchainMaintainer())

        if i < 8:
            agent.add_role(model.roles.MaliciousBlockProposer())
        else:
            agent.add_role(model.roles.BlockProposer())
        if i < 10:
            agent.add_role(model.roles.MaliciousBlockEndorser())
        else:
            agent.add_role(model.roles.BlockEndorser())

        #agent.add_role(model.roles.TransactionProposer())
        agents.append(agent)

    env = agr4bs.Environment(model.Factory)
    env.add_role(agr4bs.roles.StaticBootstrap())
    env.add_role(agr4bs.models.eth2.roles.MaliciousBlockCreatorElector())
    #env.add_role(agr4bs.models.eth2.roles.TransactionCreatorElector())

    for agent in agents:
        env.add_agent(agent)

    epoch = datetime.datetime.utcfromtimestamp(0)
    scheduler = agr4bs.Scheduler(env, model.Factory, current_time=epoch)

    def condition(environment: agr4bs.Environment) -> bool:
        return environment.date < epoch + datetime.timedelta(seconds=TIME)

    def progress(environment: agr4bs.Environment) -> bool:
        delta: datetime.timedelta = environment.date - epoch
        return min(1, delta.total_seconds() / datetime.timedelta(seconds=TIME).total_seconds())

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

    # for ref in agents:
    #     print("Head for agent " + ref.name + " : " + ref.context['blockchain'].head.hash + "height : " + str(ref.context['blockchain'].head.height))
    #     print("Knows d73de7db0e66214bc71c22665b225b40d2294c57b6c09ada16da15624182b49dheight : ", ref.context['blockchain'].get_block("d73de7db0e66214bc71c22665b225b40d2294c57b6c09ada16da15624182b49d") is not None)

    for head_hash, head_count in heads_counts.items():
        shared_percentage = 100 * head_count / len(agents)
        print("Head : " + head_hash + " shared by " + str(shared_percentage) +
              "% of the agents (height: " + str(heads_heights[head_hash]) + ")")
        assert head_count / len(agents) == 1

    for head_hash, head_height in heads_heights.items():
        assert head_height > 1

    for agent in agents:
        assert agent.context['epoch'] == N_BLOCKS // 32
        assert agent.context['slot'] == N_BLOCKS + ((JITTER / 2) // 12)

    for agent in agents:
        blockchain = agent.context['blockchain']

        for slot in range(N_BLOCKS):
            blocks = blockchain.get_blocks_for_slot(slot)

            assert len(blocks) == 1

            block = blocks[0]
            
            # if agent.name == "agent_0":
            
            #     if slot <= 32 * (N_EPOCH - 2):
            #         assert block.finalized

            #     if slot <= 32 * (N_EPOCH - 1):
            #         assert block.justified
            #     else:
            #         assert not block.justified
            #         assert not block.finalized



    def printRed(skk): print("\033[91m {}\033[00m" .format(skk))
    def printGreen(skk): print("\033[92m {}\033[00m" .format(skk))

    # Print a visualization of the blockchain
    agent = agents[0]

    # Print all the latest messages from the agent
    for message in agent.context["latest_messages"]:
        print(message)

    print("Blockchain visualization for agent " + agent.name)

    chain = []

    head = agent.context['blockchain'].head
    current = head

    while current != None:
        # Push front
        chain.insert(0, current)
        current = agent.context["blockchain"].get_block(current.parent_hash)

    for block in chain:
        print("Block : " + block.hash + " - Creator " + str(block.creator) + " - Slot : " + str(block.slot) + " - Height : " + str(block.height) + " - Contains : " + str(len(block.transactions)) + " transactions " + str(len(block.attestations)) + " attestations")
        
        for attestation in block.attestations:
            print("Attestation from : " + attestation.agent_name + " - Slot : " + str(attestation.slot))

        children = agent.context["blockchain"].get_direct_children(block)

        for child in children:
            if agent.context["blockchain"].is_block_on_main_chain(child):
                printGreen("Child : " + child.hash + " - Creator " + str(child.creator) + " - Slot : " + str(child.slot) + " - Height : " + str(child.height))
            else:
                printRed("Child : " + child.hash + " - Creator " + str(child.creator) + " - Slot : " + str(child.slot) + " - Height : " + str(child.height))
        
    print("Genesis hash : " + genesis.hash)
    print("Beacon states : " + str(len(agent.context['beacon_states'].keys())))
    print("Genesis hash in beacon states : " + str(genesis.hash in agent.context['beacon_states']))

    genesis_state = agent.context['beacon_states'][genesis.hash]
    final_state = agent.context['beacon_states'][head.hash]

    agent.process_rewards_and_penalties(final_state)

    for key in genesis_state.balances:
        if genesis_state.balances[key] != final_state.balances[key]:
            diff = final_state.balances[key] - genesis_state.balances[key]
            name = key

            if env.get_agent_by_name(key).context['malicious']:
                name = name + " (malicious)"

            if diff > 0:
                printGreen(name + " " + str(final_state.balances[key] - genesis_state.balances[key]))
            else:
                printRed(name + " " + str(final_state.balances[key] - genesis_state.balances[key]))

    honest_agents = [agent for agent in agents if not agent.context['malicious']]
    malicious_agents = [agent for agent in agents if agent.context['malicious']]

    average_honest_reward = sum([final_state.balances[agent.name] - genesis_state.balances[agent.name] for agent in honest_agents]) / len(honest_agents)
    average_malicous_reward = sum([final_state.balances[agent.name] - genesis_state.balances[agent.name] for agent in malicious_agents]) / len(malicious_agents)

    print("Average honest reward : " + str(average_honest_reward))
    print("Average malicious reward : " + str(average_malicous_reward))

    model.RLFactory.compute_rewards()

    print("attester history")
    for history in model.RLFactory.get_attester_history():
        print(history)

    print("proposer history")
    for history in model.RLFactory.get_proposer_history():
        print(history)