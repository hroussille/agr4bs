"""
Abstract implementation of the Peer role as per AGR4BS

PeerContextChange:

The PeerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

PeerEndorser:

The Peer implementation which MUST contain the following behaviors :

# TODO

"""

import random

from ..environment import Environment
from ..agents import AgentType
from ..network.messages import CreateBlock
from .role import Role, RoleType
from ..common import every, SECONDS


class BlockCreatorElector(Role):
    """
        Implementation of the Peer Role which must
        expose the following behaviors :
        - endorse_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_CREATOR_ELECTOR, AgentType.EXTERNAL_AGENT)

    @staticmethod
    @every(0.1, SECONDS)
    async def elect_block_creator(agent: Environment):
        """
            Notify a participant that it can create a block.

            This is a system event simulating a normal election process
            such as PoW or PoS potentially leading to a block proposal.
        """
        #selected = random.choice(agent.agents_names)
        selected = agent.agents_names[0]
        #selected = random.sample(agent.agents_names, 2)
        #selected = random.sample(agent.agents_names, random.randint(1, 2))
        await agent.send_system_message(CreateBlock(agent.name), selected)
