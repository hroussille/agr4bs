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
from ..network.messages import AcceptInboundPeer, DenyInboundPeer, DropInboundPeer, PeerDiscovery, RequestInboundPeer, RequestBootstrapPeers, RequestPeerDiscovery
from ..events import INIT, CLEANUP, DROP_INBOUND_PEER, DROP_OUTBOUND_PEER
from ..events import BOOTSTRAP_PEERS, REQUEST_PEER_DISCOVERY, PEER_DISCOVERY
from ..events import REQUEST_INBOUND_PEER
from ..events import ACCEPT_INBOUND_PEER, DENY_INBOUND_PEER
from ..events import SEND_MESSAGE, RECEIVE_MESSAGE
from ..agents import ExternalAgent, ContextChange, AgentType
from .role import Role, RoleType
from ..common import export, on, every


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
        self.outbound_peers_activity = {}
        self.peer_registry = set()


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
    @export
    @on(INIT)
    def send_request_bootstrap_peers(agent: ExternalAgent):
        """
            Send a request for bootstrap peers to the environment on startup.
        """
        agent.send_message(RequestBootstrapPeers(agent.name), "environment", no_drop=True)

    @staticmethod
    @export
    @on(BOOTSTRAP_PEERS)
    def bootstrap_peers(agent: ExternalAgent, candidates: list[str]):
        """
            Send a inbound peer request to all initial peer candidates

            :param agent: The agent on which the behavior operates
            :type agent: ExternalAgent
            :param candidates: the list of candidate peer addresses
            :type candidates: list[str]
        """

        for candidate in candidates:
            agent.send_request_inbound_peer(candidate)

    @staticmethod
    @export
    @on(RECEIVE_MESSAGE)
    def register_inbound_peer_activity(agent: ExternalAgent, peer: str):
        """
            Register the last time activity was witnessed from an inbound peer
        """
        agent.context['inbound_peers_activity'][peer] = agent.date

    @staticmethod
    @export
    @on(SEND_MESSAGE)
    def register_outbound_peer_activity(agent: ExternalAgent, peers: list[str]):
        """
            Register the last time activity was witnessed towards an outbound peer
        """
        for peer in peers:
            agent.context['outbound_peers_activity'][peer] = agent.date


    @staticmethod
    @export
    @every(minutes=1)
    def find_outbound_peer(agent: ExternalAgent):
        """
            Periodically look for new outbound peers if we have some connections to spare.

            If we have no known peer, request bootstrap from the Environment
            Otherwise, select a random peer from known peers that are not already inbound peers
            and send a connection request to it.
        """

        if len(agent.context['peer_registry']) == 0:
            return

        if len(agent.context['outbound_peers']) == agent.max_outbound_peers:
            return

        all_known_peers = list(agent.context['peer_registry'])
        inbounds = agent.context['inbound_peers']
        outbounds = agent.context['outbound_peers']

        valid_candidates = [
            peer for peer in all_known_peers if peer not in inbounds.union(outbounds)]

        if len(valid_candidates) == 0:
            return

        candidate = random.choice(valid_candidates)
        agent.send_request_inbound_peer(candidate)

    @staticmethod
    @export
    @every(seconds=30)
    def trigger_peer_discovery(agent: ExternalAgent):
        """
            Periodically send peer discovery requests to known peers that are not already
            inbound peers.

            The answer will be handled later to populate the peer registry.
        """

        n_outbound_peers = len(agent.context['outbound_peers'])

        if n_outbound_peers >= agent.max_outbound_peers:
            return
        if n_outbound_peers == 0:
            agent.send_request_bootstrap_peers()
        else:
            all_known_peers = list(agent.context['peer_registry'])
            inbounds = agent.context['inbound_peers']
            outbounds = agent.context['outbound_peers']

            valid_candidates = [
                peer for peer in all_known_peers if peer not in inbounds.union(outbounds)]

            if len(valid_candidates) > 1:
                selected = random.choice(valid_candidates)
                agent.send_request_peer_discovery(selected)

    @staticmethod
    @export
    def send_request_peer_discovery(agent: ExternalAgent, peer: str):
        """ Send a peer discovery request to a specific peer

            :param agent: The Agent on which the behavior operates
            :type agent: ExternalAgent
            :param peer: the address of the peer
            :type peer: str
        """
        agent.send_message(RequestPeerDiscovery(agent.name), peer)

    @staticmethod
    @export
    @on(REQUEST_PEER_DISCOVERY)
    def receive_request_peer_discovery(agent: ExternalAgent, peer: str):
        """
            Handle a REQUEST_PEER_DISCOVERY event
        """
        agent.send_message(PeerDiscovery(agent.name, agent.context['peer_registry']), peer)

    @staticmethod
    @export
    @on(PEER_DISCOVERY)
    def receive_peer_discovery(agent: ExternalAgent, new_peers: list[str]):

        """
            Behavior called on PEER_DISCOVERY event.

            The peer answers a peer_discovery_request with a list of known peers (i.e., its registry)
            which is then merged with the local registry to be used later on in order to establish new
            connections.
        """

        for peer in new_peers:
            if peer != agent.name:
                agent.context['peer_registry'].add(peer)

    @staticmethod
    @export
    def send_request_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        agent.send_message(RequestInboundPeer(agent.name), peer)

    @staticmethod
    @export
    @on(REQUEST_INBOUND_PEER)
    def receive_request_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        inbound_peers = agent.context['inbound_peers']

        if len(inbound_peers) >= agent.max_inbound_peers and peer not in inbound_peers:
            agent.send_message(DenyInboundPeer(agent.name), peer)

        else:
            inbound_peers.add(peer)
            agent.send_message(AcceptInboundPeer(agent.name), peer)

    @staticmethod
    @export
    @on(ACCEPT_INBOUND_PEER)
    def accept_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        if len(agent.context['outbound_peers']) < agent.max_outbound_peers:
            agent.context['outbound_peers'].add(peer)

    @staticmethod
    @export
    @on(DENY_INBOUND_PEER)
    def deny_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """

        if peer in agent.context['inbound_peers']:
            agent.context['inbound_peers'].remove(peer)

    @staticmethod
    @export
    def notify_drop_inbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """
        if peer in agent.context['inbound_peers']:
            agent.context['inbound_peers'].remove(peer)

        agent.send_message(DropInboundPeer(agent.name), peer)

    @staticmethod
    @export
    @on(DROP_INBOUND_PEER)
    def receive_drop_inbound_peer(agent: ExternalAgent, peer: str):
        """
            Handles a DROP_INBOUND_PEER event.
        """
        if peer in agent.context['outbound_peers']:
            agent.context['outbound_peers'].remove(peer)

    @staticmethod
    @export
    def notify_drop_outbound_peer(agent: ExternalAgent, peer: str):
        """ Send a peer request to a specific peer

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param peer: the address of the peer
            :type peer: str
        """
        if peer in agent.context['outbound_peers']:
            agent.context['outbound_peers'].remove(peer)

    @staticmethod
    @export
    @on(DROP_OUTBOUND_PEER)
    def receive_drop_outbound_peer(agent: ExternalAgent, peer: str):
        """
            Handles a DROP_OUTBOUND_PEER event.
        """
        if peer in agent.context['inbound_peers']:
            agent.context['inbound_peers'].remove(peer)
