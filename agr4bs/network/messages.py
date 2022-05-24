"""
    Core and Custom messages types definitions
"""

from enum import Enum
from ..events import REQUEST_INBOUND_PEER, ACCEPT_INBOUND_PEER, DENY_INBOUND_PEER, DROP_INBOUND_PEER
from ..events import STOP_SIMULATION


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

    PROPOSE_BLOCK = 9
    REQUEST_BLOCK = 10

    REQUEST_BLOCK_ENDORSEMENT = 11
    ACCEPT_BLOCK_ENDORSEMENT = 12
    DENY_BLOCK_ENDORSEMENT = 13

    DIFFUSE_TRANSACTION = 14
    REQUEST_TRANSACTION_ENDORSEMENT = 15
    ACCEPT_TRANSACTION_ENDORSEMENT = 16
    DENY_TRANSACTION_ENDORSEMENT = 17

    PAUSE_SIMULATION = 18
    RESTART_SIMULATION = 19
    STOP_SIMULATION = 20

    CUSTOM_MESSAGE = 21


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
