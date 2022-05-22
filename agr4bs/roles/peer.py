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
import asyncio
from agr4bs.events.events import DROP_INBOUND_PEER

from agr4bs.network.messages import AcceptInboundPeer, DenyInboundPeer, DropInboundPeer, RequestInboundPeer
from ..events import BOOTSTRAP_PEERS, UPDATE_PEERS, REQUEST_PEER_DISCOVERY
from ..events import REQUEST_INBOUND_PEER
from ..events import ACCEPT_INBOUND_PEER, DENY_INBOUND_PEER
from ..agents import ExternalAgent, ContextChange, AgentType
from .role import Role, RoleType, on


class PeerContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (Peer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        super().__init__()

        self.inbound_peers = set()
        self.inbound_peers_activity = {}
        self.outbound_peers = set()


class Peer(Role):
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
        return PeerContextChange()

    @staticmethod
    @on(BOOTSTRAP_PEERS)
    async def bootstrap_peers(agent: ExternalAgent, candidates: list[str]):
        """
            Send a inbound peer request to all initial peer candidates

            :param agent: The agent on which the behavior operates
            :type agent: ExternalAgent
            :param candidates: the list of candidate peer addresses
            :type candidates: list[str]
        """

        n = min(len(candidates), agent.max_outbound_peers)
        selected = random.sample(candidates, n)

        for candidate in selected:
            await agent.send_request_inbound_peer(agent, candidate)

    @staticmethod
    async def register_peer_activity(agent: ExternalAgent, peer: str):
        """
            Register the last time activity was witnessed from an inbound peer
        """
        current_time = asyncio.get_event_loop().time()
        agent.context['inbound_peers_activity'][peer] = current_time

    @staticmethod
    @on(UPDATE_PEERS)
    async def drop_inactive_peers(agent: ExternalAgent):
        """
            Cleanup inactive inbound peers.
        """

        current_time = asyncio.get_event_loop().time()

        for inbound_peer in agent.context['inbound_peers'].copy():
            if current_time - agent.context['inbound_peers_activity'][inbound_peer] > agent.drop_time:
                agent.context['inbound_peers'].remove(inbound_peer)
                del agent.context['inbound_peers_activity'][inbound_peer]
                await agent.notify_drop_inbound_peer(agent, inbound_peer)

    @staticmethod
    async def send_request_peer_discover(agent: ExternalAgent):
        pass

    @staticmethod
    @on(REQUEST_PEER_DISCOVERY)
    async def receive_request_peer_discovery(agent: ExternalAgent):
        pass

    @staticmethod
    async def send_request_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        await agent.send_message(RequestInboundPeer(agent.name), peer)

    @staticmethod
    @on(REQUEST_INBOUND_PEER)
    async def receive_request_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        await agent.register_peer_activity(agent, peer)

        inbound_peers = agent.context['inbound_peers']

        if len(inbound_peers) >= agent.max_inbound_peers and peer not in inbound_peers:
            await agent.send_message(DenyInboundPeer(agent.name), peer)

        else:
            inbound_peers.add(peer)
            await agent.send_message(AcceptInboundPeer(agent.name), peer)

    @staticmethod
    @on(ACCEPT_INBOUND_PEER)
    async def accept_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        await agent.register_peer_activity(agent, peer)
        agent.context['outbound_peers'].add(peer)

    @staticmethod
    @on(DENY_INBOUND_PEER)
    async def deny_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        await agent.register_peer_activity(agent, peer)

        if peer in agent.context['inbound_peers']:
            agent.context['inbound_peers'].remove(peer)

    @staticmethod
    async def notify_drop_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """
        if peer in agent.context['inbound_peers']:
            agent.context['inbound_peers'].remove(peer)

        await agent.send_message(DropInboundPeer(agent.name), peer)

    @staticmethod
    @on(DROP_INBOUND_PEER)
    async def receive_drop_inbound_peer(agent: ExternalAgent, peer: str):
        if peer in agent.context['outbound_peers']:
            agent.context['outbound_peers'].remove(peer)

    @staticmethod
    async def drop_outbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """
        if peer in agent.context['outbound_peers']:
            agent.context['outbound_peers'].remove(peer)
