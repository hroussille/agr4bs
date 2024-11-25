"""
    Ethereum 2.0 Factory file class implementation
"""

from ....blockchain import Payload
from ....network import Network
from ..blockchain import Blockchain, Block, Transaction
from ....state import State
from ...eth import VM

from .factory import Eth2Factory


class RLEth2Factory (Eth2Factory):

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
    def push_attester_history(state, action):
        RLEth2Factory.__attester_history.append((state, action))

    @staticmethod
    def push_proposer_history(state, action):
        RLEth2Factory.__proposer_history.append((state, action))

    @staticmethod
    def compute_rewards():
        # Go though the attester history and compute the rewards
        RLEth2Factory.compute_attester_rewards()


        # Go though the proposer history and compute the rewards
        RLEth2Factory.compute_proposer_rewards()


    @staticmethod
    def compute_attester_rewards():

        new_histories = []

        for history in RLEth2Factory.__attester_history:
            slot = history[0][2]
            malicious = history[1].startswith("MALICIOUS")

            # Find a matching proposer at slot N or N+1
            proposer_action = False

            for proposer_history in RLEth2Factory.__proposer_history:
                if proposer_history[0][1] == slot or proposer_history[0][1] == slot + 1:
                    proposer_action = proposer_history[1].startswith("MALICIOUS")
                    break

            if malicious and not proposer_action:
                reward = -1

            if not malicious and not proposer_action:
                reward = 0

            if malicious and proposer_action:
                reward = 1

            new_histories.append((history[0], history[1], reward))
        
        RLEth2Factory.__attester_history = new_histories

            


    @staticmethod
    def compute_proposer_rewards():

        new_histories = []

        for history in RLEth2Factory.__proposer_history:
            slot = history[0][1]
            malicious = history[1].startswith("MALICIOUS")

            # Find a matching attester at slot N or N-1
            attester_action = False

            for attester_history in RLEth2Factory.__attester_history:
                if attester_history[0][2] == slot or attester_history[0][2] == slot - 1:
                    attester_action = attester_history[1].startswith("MALICIOUS")
                    break

            if malicious and not attester_action:
                reward = -1

            if not malicious and not attester_action:
                reward = 0

            if malicious and attester_action:
                reward = 1

            new_histories.append((history[0], history[1], reward))

        RLEth2Factory.__proposer_history = new_histories
            
