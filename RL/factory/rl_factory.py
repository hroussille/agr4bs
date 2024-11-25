"""
    Ethereum 2.0 Factory file class implementation
"""

import torch
from collections import namedtuple
from agr4bs.models.eth2.factory import Factory
from agr4bs.models.eth2.constants import PARTICIPATION_FLAG_WEIGHTS

HONEST_PROPOSAL = 0
MALICIOUS_PROPOSAL = 1

HONEST_ATTESTATION = 0
MALICIOUS_ATTESTATION = 1
MALICIOUS_ATTESTATION_ON_PARENT = 1
MALICIOUS_ATTESTATION_ON_CURRENT = 2

IntermediateTransition = namedtuple('IntermediateTransition', ['state', 'action', 'slot'])
Transition = namedtuple('Transition', ['state', 'action', 'next_state', 'reward'])

class RLEth2Factory (Factory):

    """
        The Ethereum 2.0 is the core factory for all common Eth 2.0 structures
        - Blockchain
        - Block
        - Transaction
        - Payload
    """

    __attester_history = []
    __proposer_history = []

    @staticmethod
    def reset_history():
        RLEth2Factory.__attester_history = []
        RLEth2Factory.__proposer_history = []

    @staticmethod
    def get_attester_history():
        return RLEth2Factory.__attester_history
    
    @staticmethod
    def get_proposer_history():
        return RLEth2Factory.__proposer_history
    
    @staticmethod
    def push_attester_history(state, action, slot):
        RLEth2Factory.__attester_history.append(IntermediateTransition(state, action, slot))

    @staticmethod
    def push_proposer_history(state, action, slot):
        RLEth2Factory.__proposer_history.append(IntermediateTransition(state, action, slot))

    @staticmethod
    def rebuild_attester_transitions_2(agent, blockchain):
        rebuilt_transitions = []


        for index, history in enumerate(RLEth2Factory.__attester_history):
            slot = history[2]

            # Find the block of the canonical chain that included the attestation
            block = None
            attestation = None

            for _block in blockchain:
                for _attestation in _block.attestations:
                    if _attestation.slot == slot:
                        attestation = _attestation
                        block = _block
                        break

            proposer_reward = 0

            # Find the protocol reward for the block proposal that included the attestation
            if block is not None:

                # Only add a proposer reward share if this is a successfull fork
                # if block.slot == agent.context['blockchain'].get_block(block.parent_hash).slot + 2:
                before_reward = agent.context['beacon_states'][block.parent_hash]
                after_reward = agent.context['beacon_states'][block.hash]
                proposer_reward = after_reward.balances[block.creator] - before_reward.balances[block.creator]

            # Find the attester reward given at the end of the epoch
            attester_reward = 0

            # Find the block that starts the next epoch
            new_epoch_block = agent.context['blockchain'].get_checkpoint_from_epoch(block.epoch + 1, blockchain[-1])
            beacon_state = agent.context['beacon_states'][new_epoch_block.hash]
            flag_deltas = [agent.get_flag_index_deltas(beacon_state, flag_index) for flag_index in range(len(PARTICIPATION_FLAG_WEIGHTS))]

            for (rewards, penalties) in flag_deltas:
                attester_reward += rewards[attestation.agent_name] - penalties[attestation.agent_name]
            
            next_state = None

            if index + 1 < len(RLEth2Factory.__attester_history):
                next_state = RLEth2Factory.__attester_history[index + 1][0]

            rebuilt_transitions.append(Transition(history[0], history[1], next_state, torch.tensor([attester_reward + proposer_reward / 2])))

        return rebuilt_transitions
    
    @staticmethod
    def rebuild_proposer_transitions_2(agent, blockchain):
        rebuilt_transitions = []

        for index, history in enumerate(RLEth2Factory.__proposer_history):
            slot = history[2]

            # Find the block of the canonical chain that was produced at this slot
            block = None

            for _block in blockchain:
                if _block.slot == slot:
                    block = _block
                    break

            proposer_reward = 0

            # Find the protocol reward for the block proposal that included the attestation
            if block is not None:
                before_reward = agent.context['beacon_states'][block.parent_hash]
                after_reward = agent.context['beacon_states'][block.hash]
                proposer_reward = after_reward.balances[block.creator] - before_reward.balances[block.creator]
            # else:
            #     # No block in the canonical chain : this is a failed fork, penalize the proposer by the reward of the previous block
            #     for _block in blockchain:
            #         if _block.slot == slot - 1:
            #             block = _block
            #             break

            #     before_reward = agent.context['beacon_states'][block.parent_hash]
            #     after_reward = agent.context['beacon_states'][block.hash]
            #     proposer_reward = before_reward.balances[block.creator] - after_reward.balances[block.creator]
            
            next_state = None

            if index + 1 < len(RLEth2Factory.__proposer_history):
                next_state = RLEth2Factory.__proposer_history[index + 1][0]

            rebuilt_transitions.append(Transition(history[0], history[1], next_state, torch.tensor([proposer_reward])))

        return rebuilt_transitions


    @staticmethod
    def rebuild_attester_transitions(average_gain):
        rebuilt_transitions = []

        for index, history in enumerate(RLEth2Factory.__attester_history):
            slot = history[2]
            attester_action = history[1].item()

            # Find a matching proposer at slot N or N+1
            proposer_action = HONEST_PROPOSAL
            proposer_slot = None

            for proposer_history in RLEth2Factory.__proposer_history:
                if proposer_history[2] == slot or proposer_history[2] == slot + 1:
                    proposer_action = proposer_history[1].item()
                    proposer_slot = proposer_history[2]
                    break

            reward = 0

            # if proposer_slot is None:
            #     # If there was no malicious proposer at slot N or N + 1 and the attester was malicious
            #     if attester_action != HONEST_ATTESTATION:
            #         reward = -1
            
            #     # If there was no malicious proposer at slot N or N + 1 and the attester was honest
            #     if attester_action == HONEST_ATTESTATION:
            #         reward = 0

            # if proposer_slot is not None:
            #     # If there was a malicious proposer at slot N or N + 1 and they were both malicious
            #     if attester_action == MALICIOUS_ATTESTATION and proposer_action == MALICIOUS_PROPOSAL:
            #         reward = 1
                
            #     # If there was a malicious proposer at slot N or N + 1 and they were both honest
            #     if attester_action == HONEST_ATTESTATION and proposer_action == HONEST_PROPOSAL:
            #         reward = 0
                
            #     # If there was a malicious proposer at slot N or N + 1 and they disagreed
            #     if attester_action != proposer_action:
            #         reward = -1

            reward = torch.tensor([reward])

            next_state = None

            if index + 1 < len(RLEth2Factory.__attester_history):
                next_state = RLEth2Factory.__attester_history[index + 1][0]
            else:
               reward = torch.tensor([average_gain])

            rebuilt_transitions.append(Transition(history[0], history[1], next_state, reward))

        return rebuilt_transitions

    @staticmethod
    def rebuild_proposer_transitions(average_gain):
        rebuilt_transitions = []

        for index, history in enumerate(RLEth2Factory.__proposer_history):
            slot = history[2]
            proposer_action = history[1].item()

            # Find a matching attester at slot N or N-1
            attester_action = HONEST_ATTESTATION
            attester_slot = None

            for attester_history in RLEth2Factory.__attester_history:
                if attester_history[2] == slot or attester_history[2] == slot - 1:
                    attester_action = attester_history[1].item()
                    break

            reward = 0

            # # If there was no malicious attester found, assume honest attestation
            # if attester_slot is None:
            #     if proposer_action != HONEST_ATTESTATION:
            #         reward = -1
            #     if proposer_action == HONEST_ATTESTATION:
            #         reward = 0

            # if attester_slot is not None:
            #     # If there was a malicious attester at slot N or N - 1 and they were both malicious
            #     if attester_action == MALICIOUS_ATTESTATION and proposer_action == MALICIOUS_PROPOSAL:
            #         reward = 1
                
            #     # If there was a malicious attester at slot N or N - 1 and they were both honest
            #     if attester_action == HONEST_ATTESTATION and proposer_action == HONEST_PROPOSAL:
            #         reward = 0
                
            #     # If there was a malicious attester at slot N or N - 1 and they disagreed
            #     if attester_action != proposer_action:
            #         reward = -1

            next_state = None

            reward = torch.tensor([reward])

            if index + 1 < len(RLEth2Factory.__proposer_history):
                next_state = RLEth2Factory.__proposer_history[index + 1][0]
            else:
               reward = torch.tensor([average_gain])

            rebuilt_transitions.append(Transition(history[0], history[1], next_state, reward))

        return rebuilt_transitions