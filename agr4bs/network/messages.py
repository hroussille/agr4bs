"""
    Core and Custom messages types definitions
"""

from enum import Enum

from ..events import REQUEST_PEER_DISCOVERY, PEER_DISCOVERY
from ..events import REQUEST_BOOTSTRAP_PEERS, BOOTSTRAP_PEERS
from ..events import REQUEST_INBOUND_PEER, ACCEPT_INBOUND_PEER, DENY_INBOUND_PEER, DROP_INBOUND_PEER
from ..events import STOP_SIMULATION
from ..events import CREATE_BLOCK, RECEIVE_BLOCK

from ..blockchain import Block


class MessageType(Enum):

    """
        Enumeration of the allowed message types
    """

    REQUEST_INBOUND_PEER = 1
    ACCEPT_INBOUND_PEER = 2
    DENY_INBOUND_PEER = 3
    DROP_INBOUND_PEER = 4

    REQUEST_OUTBOUND_PEER = 5
    ACCEPT_OUTBOUND_PEER = 6
    DENY_OUTBOUND_PEER = 7
    DROP_OUTBOUND_PEER = 8

    CREATE_BLOCK = 9
    REQUEST_BLOCK = 10
    PROPOSE_BLOCK = 11
    DIFFUSE_BLOCK = 12

    REQUEST_BLOCK_ENDORSEMENT = 13
    ACCEPT_BLOCK_ENDORSEMENT = 14
    DENY_BLOCK_ENDORSEMENT = 15

    DIFFUSE_TRANSACTION = 16
    REQUEST_TRANSACTION_ENDORSEMENT = 17
    ACCEPT_TRANSACTION_ENDORSEMENT = 18
    DENY_TRANSACTION_ENDORSEMENT = 19

    PAUSE_SIMULATION = 20
    RESTART_SIMULATION = 21
    STOP_SIMULATION = 22

    CUSTOM_MESSAGE = 23

    REQUEST_BOOTSTRAP_PEERS = 24
    BOOTSTRAP_PEERS = 25

    REQUEST_PEER_DISCOVERY = 26
    PEER_DISCOVERY = 26


class Message:

    """
        A Message represents some informations sent from an Agent to one
        or many other Agents. It may contain arbitrary data and trigger
        a specific event on reception.
    """

    def __init__(self, origin: str, _type: MessageType, event: str, *args):
        self._origin = origin
        self._type = _type
        self._event = event
        self._data = args

    @property
    def origin(self):
        """
            Get the origin of the message
        """
        return self._origin

    @property
    def type(self):
        """
            Get the type of the Message
        """
        return self._type

    @property
    def event(self):
        """
            Get the event that should be fired on reception of the Message
        """
        return self._event

    @property
    def data(self):
        """
            Get the data contained in the Message
        """
        return self._data


class RequestBootstrapPeers(Message):

    """
        Message sent when an Agent whishes to get a list of bootstraping
        peer nodes in the Network.
    """

    def __init__(self, origin: str):
        _type = MessageType.REQUEST_BOOTSTRAP_PEERS
        _event = REQUEST_BOOTSTRAP_PEERS
        super().__init__(origin, _type, _event, origin)


class BootStrapPeers(Message):

    """
        Message sent to agents to give them the list of bootstraping nodes
    """

    def __init__(self, origin: str, bootstrap_list: list[str]):
        _type = MessageType.BOOTSTRAP_PEERS
        _event = BOOTSTRAP_PEERS
        super().__init__(origin, _type, _event, bootstrap_list)


class RequestPeerDiscovery(Message):

    """
        Message sent to other agents to request peer discovery
    """

    def __init__(self, origin: str):
        _type = MessageType.REQUEST_PEER_DISCOVERY
        _event = REQUEST_PEER_DISCOVERY
        super().__init__(origin, _type, _event, origin)


class PeerDiscovery(Message):

    """
        Message sent to an agent that previously requested peer discovery
    """

    def __init__(self, origin: str, peers: list[str]):
        _type = MessageType.PEER_DISCOVERY
        _event = PEER_DISCOVERY
        super().__init__(origin, _type, _event, peers)


class RequestInboundPeer(Message):

    """
        Message sent when an Agent (1) whishes to connect
        to another Agent (2).

        (1) states its intention to become and inbound peer of (2)
    """

    def __init__(self, origin: str):
        _type = MessageType.REQUEST_INBOUND_PEER
        _event = REQUEST_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class AcceptInboundPeer(Message):

    """
        Message sent when an Agent (1) accepts the connection
        request from another Agent (2)
    """

    def __init__(self, origin: str):
        _type = MessageType.ACCEPT_INBOUND_PEER
        _event = ACCEPT_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DenyInboundPeer(Message):

    """
        Message sent when an Agent (1) denies the connection
        request from another Agent (2)
    """

    def __init__(self, origin: str):
        _type = MessageType.DENY_INBOUND_PEER
        _event = DENY_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DropInboundPeer(Message):

    """
        Message sent when an Agent (1) notifies another Agent (2)
        that the connection between them will no longer be maintained
        by (1)
    """

    def __init__(self, origin: str):
        _type = MessageType.DROP_INBOUND_PEER
        _event = DROP_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class StopSimulation(Message):

    """
        Message sent to notify an Agent that the Simulation
        should come to an end.
    """

    def __init__(self, origin: str):
        _type = MessageType.STOP_SIMULATION
        _event = STOP_SIMULATION
        super().__init__(origin, _type, _event)


class CreateBlock(Message):

    """
        System Message sent to notify an agent that it can create
        a Block.
    """

    def __init__(self, origin: str):
        _type = MessageType.CREATE_BLOCK
        _event = CREATE_BLOCK
        super().__init__(origin, _type, _event)


class ProposeBlock(Message):

    """
        Message sent to propose a newly created block to other participants.
    """

    def __init__(self, origin: str, block: Block):
        _type = MessageType.PROPOSE_BLOCK
        _event = RECEIVE_BLOCK
        super().__init__(origin, _type, _event, Block.from_serialized(block.serialize()))


class DiffuseBlock(Message):

    """
        Message sent to diffuse a block to the network
    """

    def __init__(self, origin: str, block: Block):
        _type = MessageType.PROPOSE_BLOCK
        _event = RECEIVE_BLOCK
        super().__init__(origin, _type, _event, Block.from_serialized(block.serialize()))
