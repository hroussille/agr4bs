
"""
Ethereum 2.0 implementation of the Peer role as per AGR4BS
"""
import random
import more_itertools
from ....environment import Environment
from ....agents import AgentType, ContextChange
from ....network.messages import CreateBlock, NextEpoch, NextSlot
from ....roles import Role, RoleType
from ....common import export, every, on
from ....events.events import INIT
from ..constants import SLOTS_PER_EPOCH


class MaliciousBlockCreatorElectorContextChange(ContextChange):

    """
        Context changes that need to be made to the ExternalAgent when
        the associated Role (BlockchainMaintainer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.epoch: int = -1
        self.slot: int = 0
        self.block_proposers = []
        self.block_attesters = []
        self.attesters = []


class MaliciousBlockCreatorElector(Role):

    """
        Ethereum 2.0 block creator elector implementation

        This class manages both the Ethereum 2.0 clock along epochs and slots and
        maintains the list of scheduled block proposers to instruct them to create
        a new block whenever they should do so.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_CREATOR_ELECTOR, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return MaliciousBlockCreatorElectorContextChange()

    @staticmethod
    @export
    @on(INIT)
    def initialize(agent: Environment):
        """
            Initialize the environment's clock (epoch and slot)
        """
        agent.next_epoch()
        
    @staticmethod
    @export
    def next_epoch(agent: Environment):
        """
            Move all agents to the next epoch and compute the new block proposers list
        """

        agents = [agent.get_agent_by_name(agent_name) for agent_name in agent.agents_names]
        malicious_agents = [agent for agent in agents if agent.context['malicious'] is True]
        malicious_proposers = [agent for agent in agents if agent.context['malicious_proposer'] is True]
        honest_proposers = [agent for agent in agents if not agent.context['malicious_proposer']]
        malicious_attesters = [agent for agent in agents if agent.context['malicious_attester'] is True]
        honest_attesters = [agent for agent in agents if not agent.context['malicious_attester']]

        agent.context['epoch'] = agent.context['epoch'] + 1
        agents = random.sample(agent.agents_names, len(agent.agents_names))

        proposers = []

        print("Number of agents : ", len(agent.agents_names))
        print("Number of malicious agents : ", len(malicious_agents))
        print("Number of malicious proposers : ", len(malicious_proposers))
        print("Number of honest proposers : ", len(honest_proposers))
        print("Number of malicious attesters : ", len(malicious_attesters))
        print("Number of honest attesters : ", len(honest_attesters))

        malicious_proposer_index = 0
        honest_proposer_index = 0
        malicious_attester_index = 0
        honest_attester_index = 0

        # Always start with two honest block proposer, place the malicious ones 3 slots apart from each other after than
        # Malicious proposers have slots 2, 6, 10, 14, 18, 22, 26, 30
        # Honest ones have slots 0, 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 16, 17, 19, 20, 21, 23, 24, 25, 27, 28, 29, 31
        for i in range(32):

            print("hon_proposer_index : ", honest_proposer_index)
            print("mal_proposer_index : ", malicious_proposer_index)

            if i < 2:
                proposers.append(honest_proposers[honest_proposer_index].name)
                honest_proposer_index += 1
            else:
                if i % 4 == 2:
                    proposers.append(malicious_proposers[malicious_proposer_index].name)
                    malicious_proposer_index += 1
                else:
                    proposers.append(honest_proposers[honest_proposer_index].name)
                    honest_proposer_index += 1


        # Always start with two honest block proposer, place the malicious ones 2 slots apart from each other after than
        # Malicious proposers have slots 2, 5, 8, 11, 14, 17, 20, 23, 26, 29
        # Honest ones have slots 0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22, 24, 25, 27, 28, 30, 31
        agent.context['block_attesters'] = []

        for i in range(32):
            if i < 2:
                agent.context['block_attesters'].append([honest_attesters[honest_attester_index].name])
                honest_attester_index += 1
            else:
                if i % 3 == 2:
                    agent.context['block_attesters'].append([malicious_attesters[malicious_attester_index].name])
                    malicious_attester_index += 1
                else:
                    agent.context['block_attesters'].append([honest_attesters[honest_attester_index].name])
                    honest_attester_index += 1

        agent.context['block_proposers'] = proposers
        agent.send_system_message(NextEpoch(agent.name, agent.context['epoch']), agent.agents_names)

        for i in range(32):
            print("Slot ", i, " : ", agent.context['block_proposers'][i], " / ", agent.context['block_attesters'][i])

    @staticmethod
    @export
    @every(seconds=12)
    def next_slot(agent: Environment):
        """
            Move all agents to the next slot and potentiall call next_epoch if required
            Finally, instruct the current slot's block proposer to create a block
        """
        slot = (agent.context['slot'] + 1)

        agent.context['slot'] = slot

        if slot % 32 == 0:
            agent.next_epoch()

        proposer = agent.context['block_proposers'][slot % 32]
        _proposer = agent.get_agent_by_name(proposer)

        if (_proposer.context['malicious_proposer']):
            has_malicious_attester_at_same_slot = agent.get_agent_by_name(agent.context['block_attesters'][slot % 32][0]).context['malicious_attester']
            has_malicious_attester_before_slot = agent.get_agent_by_name(agent.context['block_attesters'][(slot - 1) % 32][0]).context['malicious_attester']
            _proposer.context['has_malicious_attester'] = has_malicious_attester_at_same_slot or has_malicious_attester_before_slot

        agent.send_system_message(NextSlot(agent.name, slot, agent.context['block_attesters'][slot % 32]), agent.agents_names)
        agent.send_system_message(CreateBlock(agent.name), proposer)

        same_time_as_malicious_proposer = agent.get_agent_by_name(proposer).context['malicious_proposer'] is True
        before_malicious_proposer = agent.get_agent_by_name(agent.context['block_proposers'][(slot + 1) % 32]).context['malicious_proposer'] is True
        
        current_attesters = agent.context['block_attesters'][slot % 32]

        for current_attester in current_attesters:
            target = agent.get_agent_by_name(current_attester)

            if target.context['malicious_attester']:
                target.context['next_proposer_is_malicious'] = before_malicious_proposer
                target.context['current_proposer_is_malicious'] = same_time_as_malicious_proposer
            else:
                target.context['next_proposer_is_malicious'] = False
                target.context['current_proposer_is_malicious'] = False
     
