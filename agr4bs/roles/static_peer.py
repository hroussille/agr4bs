"""
Abstract implementation of the Peer role as per AGR4BS

PeerContextChange:

The PeerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

PeerEndorser:

The Peer implementation which MUST contain the following behaviors :

# TODO

"""

from ..common import on
from ..network.messages import RequestBootstrapStaticPeers
from ..events import INIT, BOOTSTRAP_STATIC_PEERS
from ..agents import ExternalAgent, ContextChange, AgentType
from .role import Role, RoleType


class StaticPeerContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (Peer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        super().__init__()

        self.inbound_peers = set()
        self.outbound_peers = set()


class StaticPeer(Role):
    """
        Implementation of the Peer Role which must
        expose the following behaviors :
        - endorse_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.PEER, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return StaticPeerContextChange()

    @staticmethod
    @on(INIT)
    async def send_request_bootstrap_static_peers(agent: ExternalAgent):
        """
            Send a request for bootstrap static peers to the environment on startup.
        """
        await agent.send_message(RequestBootstrapStaticPeers(agent.name), "environment", no_drop=True)

    @staticmethod
    @on(BOOTSTRAP_STATIC_PEERS)
    async def bootstrap_static_peers(agent: ExternalAgent, inbounds: list[str], outbounds: list[str]):
        """
            Register the static peers as given.

            :param agent: The agent on which the behavior operates
            :type agent: ExternalAgent
            :param inbounds: the list of inbound peers
            :type inbounds: list[str]
            :param outbounds: the list of outbound peers
            :type outbounds: list[str]
        """
        for inbound in inbounds:
            agent.context['inbound_peers'].add(inbound)

        for outbound in outbounds:
            agent.context['outbound_peers'].add(outbound)
