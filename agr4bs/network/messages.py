from enum import Enum
from ..events import *


class MessageType(Enum):

    REQUEST_INBOUND_PEER = "request_inbound_peer"
    ACCEPT_INBOUND_PEER = "accept_inbound_peer"
    DENY_INBOUND_PEER = "deny_inbound_peer"
    DROP_INBOUND_PEER = "drop_inbound_peer"

    REQUEST_OUTBOUND_PEER = "request_outbound_peer"
    ACCEPT_OUTBOUND_PEER = "accept_outbound_peer"
    DENY_OUTBOUND_PEER = "deny_outbound_peer"
    DROP_OUTBOUND_PEER = "drop_outbound_peer"

    PROPOSE_BLOCK = "propose_block"
    REQUEST_BLOCK = "request_block"

    REQUEST_BLOCK_ENDORSEMENT = "request_block_endorsement"
    ACCEPT_BLOCK_ENDORSEMENT = "accept_block_endorsement"
    DENY_BLOCK_ENDORSEMENT = "deny_block_endorsement"

    DIFFUSE_TRANSACTION = "diffuse_transaction"
    REQUEST_TRANSACTION_ENDORSEMENT = "request_transaction_endorsement"
    ACCEPT_TRANSACTION_ENDORSEMENT = "accept_transaction_endorsement"
    DENY_TRANSACTION_ENDORSEMENT = "deny_transaction_endorsement"

    PAUSE_SIMULATION = "pause_simulation"
    RESTART_SIMULATION = "restart_simulation"
    STOP_SIMULATION = "stop_simulation"

    CUSTOM_MESSAGE = "custom_message"


class Message:

    def __init__(self, origin: str, _type: MessageType, event: str, *args):
        self._origin = origin
        self._type = _type
        self._event = event
        self._data = args

    @property
    def origin(self):
        return self._origin

    @property
    def type(self):
        return self._type

    @property
    def event(self):
        return self._event

    @property
    def data(self):
        return self._data


class RequestInboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.REQUEST_INBOUND_PEER
        _event = REQUEST_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class AcceptInboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.ACCEPT_INBOUND_PEER
        _event = ACCEPT_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DenyInboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.DENY_INBOUND_PEER
        _event = DENY_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DropInboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.DROP_INBOUND_PEER
        _event = DROP_INBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class RequestOutboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.REQUEST_OUTBOUND_PEER
        _event = REQUEST_OUTBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class AcceptOutboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.ACCEPT_OUTBOUND_PEER
        _event = ACCEPT_OUTBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DenyOutboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.DENY_OUTBOUND_PEER
        _event = DENY_OUTBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class DropOutboundPeer(Message):

    def __init__(self, origin: str):
        _type = MessageType.DROP_OUTBOUND_PEER
        _event = DROP_OUTBOUND_PEER
        super().__init__(origin, _type, _event, origin)


class StopSimulation(Message):

    def __init__(self, origin: str):
        _type = MessageType.STOP_SIMULATION
        _event = STOP_SIMULATION
        super().__init__(origin, _type, _event)
