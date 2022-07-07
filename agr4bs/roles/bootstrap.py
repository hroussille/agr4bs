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
from ..network.messages import BootStrapPeers
from ..events import REQUEST_BOOTSTRAP_PEERS
from .role import Role, RoleType
from ..common import on, export


class Bootstrap(Role):
    """
        Implementation of the Peer Role which must
        expose the following behaviors :
        - endorse_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.BOOTSTRAP, AgentType.EXTERNAL_AGENT)

    @staticmethod
    @export
    @on(REQUEST_BOOTSTRAP_PEERS)
    def bootstrap_peers(agent: Environment, peer: str):
        """
            Send a inbound peer request to all initial peer candidates

            :param agent: The agent on which the behavior operates
            :type agent: ExternalAgent
            :param candidates: the list of candidate peer addresses
            :type candidates: list[str]
        """
        candidates = [name for name in agent.agents_names if name != peer]
        n = min(len(candidates), 10)
        selected = random.sample(candidates, n)

        agent.send_message(BootStrapPeers(agent.name, selected), peer, no_drop=True)
