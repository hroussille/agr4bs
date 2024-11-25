
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


class BlockCreatorElectorContextChange(ContextChange):

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


class BlockCreatorElector(Role):

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
        return BlockCreatorElectorContextChange()

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

        agent.context['epoch'] = agent.context['epoch'] + 1
        agents = random.sample(agent.agents_names, len(agent.agents_names))
        proposers = random.sample(agent.agents_names, 32)

        agent.context['block_attesters'] = []
        for chunk in more_itertools.divide(32, agents):
            agent.context['block_attesters'].append(list(chunk))

        agent.context['block_proposers'] = proposers

        agent.send_system_message(NextEpoch(agent.name, agent.context['epoch']), agent.agents_names)

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
        agent.send_system_message(NextSlot(agent.name, slot, agent.context['block_attesters'][slot % 32]), agent.agents_names)
        agent.send_system_message(CreateBlock(agent.name), proposer)
