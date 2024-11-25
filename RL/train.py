"""
    Test suite for the Environment class related to agents addition
"""

import datetime
import random
from collections import Counter, namedtuple
import torch
import math
import matplotlib.pyplot as plt
import argparse
import os

from roles.malicious_block_creator_elector import MaliciousBlockCreatorElector
from roles.malicious_block_endorser import MaliciousBlockEndorser
from roles.malicious_block_proposer import MaliciousBlockProposer
from factory.rl_factory import RLEth2Factory
from utils.utils import get_forks, get_blockchain, print_blockchain

import agr4bs
from agr4bs.models.eth2.blockchain import Transaction, Block
from rl.replay_memory import ReplayMemory
from rl.network import DQN

N_BLOCKS = 32
JITTER = 12
TIME = N_BLOCKS * 12 + JITTER
BATCH_SIZE = 128
GAMMA = 0.8
EPS_START = 0.9
EPS_END = 0.01
EPS_DECAY = 2000
TAU = 0.005
LR = 1e-3
N_EPOCH = 500

PROPOSER_OBSERVATIONS = 2 
PROPOSER_ACTIONS = 2

ATTESTER_OBSERVATIONS = 2
ATTESTER_ACTIONS = 2

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

proposer_steps_done = 0
attester_steps_done = 0

episode_durations = []

def soft_update(policy_net, target_net):
    # Soft update of the target network's weights
    # θ′ ← τ θ + (1 −τ )θ′
    target_net_state_dict = target_net.state_dict()
    policy_net_state_dict = policy_net.state_dict()

    for key in policy_net_state_dict:
        target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)

    target_net.load_state_dict(target_net_state_dict)

def optimize_model(memory, policy_net, target_net, optimizer):
    if len(memory) < BATCH_SIZE:
        return
    
    transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)

    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1).values
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = torch.nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()

def main():
    """
        Test that the environment can be run and stopped later
        with no error or unwaited tasks
    """

    # Parse the arguments
    parser = argparse.ArgumentParser(description='Train the RL model')
    parser.add_argument('--result-folder', type=str, help='Folder to save the results to')
    parser.add_argument('--n-runs', type=int, help='Number of runs to perform')
    parser.add_argument('--reward', type=str, help='Reward function to use', choices=["average", "forks"])

    args = parser.parse_args()

    # Create the result folder if it does not exist
    if not os.path.exists(args.result_folder):
        os.makedirs(args.result_folder)
    else:
        raise ValueError("The result folder already exists")

    print("Starting the training")
    print("Number of runs : " + str(args.n_runs))

    for n_run in range(args.n_runs):

        proposer_replay_memory = ReplayMemory(2000)
        proposer_policy_network = DQN(PROPOSER_OBSERVATIONS, PROPOSER_ACTIONS)
        proposer_target_network = DQN(PROPOSER_OBSERVATIONS, PROPOSER_ACTIONS)
        proposer_target_network.load_state_dict(proposer_policy_network.state_dict())
        proposer_optimizer = torch.optim.AdamW(proposer_policy_network.parameters(), lr=LR, amsgrad=True)

        attester_replay_memory = ReplayMemory(2000)
        attester_policy_network = DQN(ATTESTER_OBSERVATIONS, ATTESTER_ACTIONS)
        attester_target_network = DQN(ATTESTER_OBSERVATIONS, ATTESTER_ACTIONS)
        attester_target_network.load_state_dict(attester_policy_network.state_dict())
        attester_optimizer = torch.optim.AdamW(attester_policy_network.parameters(), lr=LR, amsgrad=True)

        epoch_history = []

        def select_proposer_action(state, deterministic=False):
            global proposer_steps_done
            sample = random.random()
            eps_threshold = EPS_END + (EPS_START - EPS_END) * \
                math.exp(-1. * proposer_steps_done / EPS_DECAY)
            proposer_steps_done += 1
            if sample > eps_threshold or deterministic:
                with torch.no_grad():
                    # t.max(1) will return the largest column value of each row.
                    # second column on max result is index of where max element was
                    # found, so we pick action with the larger expected reward.
                    return proposer_policy_network(state).max(1).indices.view(1, 1)
            else:
                return torch.tensor([[random.randint(0, PROPOSER_ACTIONS - 1)]], dtype=torch.long)
            
        def select_attester_action(state, deterministic=False):
            global attester_steps_done
            sample = random.random()
            eps_threshold = EPS_END + (EPS_START - EPS_END) * \
                math.exp(-1. * attester_steps_done / EPS_DECAY)
            attester_steps_done += 1
            if sample > eps_threshold or deterministic:
                with torch.no_grad():
                    # t.max(1) will return the largest column value of each row.
                    # second column on max result is index of where max element was
                    # found, so we pick action with the larger expected reward.
                    return attester_policy_network(state).max(1).indices.view(1, 1)
            else:
                return torch.tensor([[random.randint(0, ATTESTER_ACTIONS - 1)]], dtype=torch.long)
        

        random.seed(random.randint(0, 1000))

        for _ in range(N_EPOCH):
            nb_agents = 32
            model = agr4bs.models.eth2
            factory = RLEth2Factory

            # Reset the network
            factory.build_network(reset=True)

            # Reset the histories
            factory.reset_history()

            # Fund all agents with 32 ETH
            account_transactions = [Transaction("genesis", f"agent_{i}", i, 0, 32 * 10 ** 18) for i in range(nb_agents)]

            # Make all agents validators by depositing 32 ETH into the deposit contract
            deposit_transactions = [Transaction(f"agent_{i}", "deposit_contract", 0, 0, 32 * 10 ** 18) for i in range(nb_agents)]

            genesis = Block(None, "genesis", 0, account_transactions + deposit_transactions)
            
            agents = []

            # Build the agents
            # 8 Malicious block proposers
            # 10 Malicious block attesters
            for i in range(nb_agents):
                agent = agr4bs.ExternalAgent(
                    f"agent_{i}", genesis, factory)
                agent.add_role(agr4bs.roles.StaticPeer())
                agent.add_role(model.roles.BlockchainMaintainer())

                if i < 8:
                    # Add the malicious role and inject the proposer strategy which uses the neural network
                    agent.add_role(MaliciousBlockProposer())
                    agent.context['proposer_strategy'] = select_proposer_action
                else:
                    agent.add_role(model.roles.BlockProposer())
                if i < 10:
                    # Add the malicious role and inject the attester strategy which uses the neural network
                    agent.add_role(MaliciousBlockEndorser())
                    agent.context['attester_strategy'] = select_attester_action
                else:
                    agent.add_role(model.roles.BlockEndorser())

                agents.append(agent)

            # Build the environment
            env = agr4bs.Environment(model.Factory)
            env.add_role(agr4bs.roles.StaticBootstrap())
            env.add_role(MaliciousBlockCreatorElector())

            for agent in agents:
                env.add_agent(agent)

            epoch = datetime.datetime.utcfromtimestamp(0)
            scheduler = agr4bs.Scheduler(env, model.Factory, current_time=epoch)

            def condition(environment: agr4bs.Environment) -> bool:
                return environment.date < epoch + datetime.timedelta(seconds=TIME)

            def progress(environment: agr4bs.Environment) -> bool:
                delta: datetime.timedelta = environment.date - epoch
                return min(1, delta.total_seconds() / datetime.timedelta(seconds=TIME).total_seconds())

            # Initialize and run the simulation until the stop condition is met
            scheduler.init()
            #scheduler.run(condition, progress=progress)
            scheduler.run(condition)

            heads = [agent.context['blockchain'].head for agent in agents]
            heads_hashes = [head.hash for head in heads]
            heads_counts = Counter(heads_hashes)

            # Ensure that the head is consensual
            for _, head_count in heads_counts.items():
                assert head_count / len(agents) == 1

            agent = agents[0]
            head = agent.context['blockchain'].head

            genesis_state = agent.context['beacon_states'][genesis.hash]
            final_state = agent.context['beacon_states'][head.hash]

            # agent.process_rewards_and_penalties(final_state)

            honest_agents = [agent for agent in agents if not agent.context['malicious']]
            malicious_agents = [agent for agent in agents if agent.context['malicious']]

            average_honest_reward = sum([final_state.balances[agent.name] - genesis_state.balances[agent.name] for agent in honest_agents]) / len(honest_agents)
            average_malicous_reward = sum([final_state.balances[agent.name] - genesis_state.balances[agent.name] for agent in malicious_agents]) / len(malicious_agents)

            print("Average honest reward : " + str(average_honest_reward))
            print("Average malicious reward : " + str(average_malicous_reward))

            successfull_forks, failed_forks = get_forks(agent)
            print("Successfull forks : " + str(successfull_forks) + " - Failed forks : " + str(failed_forks)) 

            if args.reward == "forks":
                reward = successfull_forks - failed_forks
            elif args.reward == "average":
                reward = average_malicous_reward
            else:
                raise ValueError("The reward function is not supported")
            #blockchain = get_blockchain(agent)
        
            #print_blockchain(agent)

            # for transition in factory.rebuild_attester_transitions_2(agent, blockchain):
            #     attester_replay_memory.push(transition)

            # for transition in factory.rebuild_proposer_transitions_2(agent, blockchain):
            #     proposer_replay_memory.push(transition)

            for transition in factory.rebuild_attester_transitions(reward):
                attester_replay_memory.push(transition)

            for transition in factory.rebuild_proposer_transitions(reward):
                proposer_replay_memory.push(transition)

            optimize_model(proposer_replay_memory, proposer_policy_network, proposer_target_network, proposer_optimizer)
            optimize_model(attester_replay_memory, attester_policy_network, attester_target_network, attester_optimizer)

            soft_update(proposer_policy_network, proposer_target_network)
            soft_update(attester_policy_network, attester_target_network)

            epoch_history.append([successfull_forks, failed_forks, average_honest_reward, average_malicous_reward])

        # Plot the history of rewards save it to a file
        # plt.title("Average malicious vs honest reward")
        # plt.xlabel("Epoch")
        # plt.ylabel("Reward (Gwei)")
        # plt.plot([i for i in range(N_EPOCH)], [history[2] for history in epoch_history], label="Honest")
        # plt.plot([i for i in range(N_EPOCH)], [history[3] for history in epoch_history], label="Malicious")
        # plt.legend()
        # plt.savefig("rewards.png")
        # plt.show()

        # Plot the history of forks save it to a file
        # plt.title("Forks")
        # plt.xlabel("Epoch")
        # plt.ylabel("Forks")
        # plt.plot([i for i in range(N_EPOCH)], [history[0] for history in epoch_history], label="Successfull")
        # plt.plot([i for i in range(N_EPOCH)], [history[1] for history in epoch_history], label="Failed")
        # plt.legend()
        # plt.savefig("forks.png")
        # plt.show()

        file_path = os.path.join(args.result_folder, f"run_{n_run}")

        # Save the data to a file
        with open(file_path + ".csv", "w") as f:
            f.write("Successfull forks, Failed forks, Average honest reward, Average malicious reward\n")
            for history in epoch_history:
                f.write(f"{history[0]},{history[1]},{history[2]},{history[3]}\n")

if __name__ == "__main__":
    main()