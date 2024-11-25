"""
    Core and Custom messages types definitions
"""

from ..blockchain.block import IBlockHeader
from ..events import CREATE_TRANSACTION, RECEIVE_TRANSACTION
from ..events import REQUEST_BOOTSTRAP_STATIC_PEERS, BOOTSTRAP_STATIC_PEERS
from ..events import REQUEST_PEER_DISCOVERY, PEER_DISCOVERY
from ..events import REQUEST_BOOTSTRAP_PEERS, BOOTSTRAP_PEERS
from ..events import REQUEST_INBOUND_PEER, ACCEPT_INBOUND_PEER, DENY_INBOUND_PEER, DROP_INBOUND_PEER
from ..events import STOP_SIMULATION
from ..events import CREATE_BLOCK, RECEIVE_BLOCK, REQUEST_BLOCK, RECEIVE_BLOCK_HEADER
from ..events import RUN_SCHEDULABLE
from ..events import REQUEST_BLOCK_ENDORSEMENT, RECEIVE_BLOCK_ENDORSEMENT
from ..events import NEXT_EPOCH, NEXT_SLOT
from ..common import Serializable


class Message:

    """
        A Message represents some informations sent from an Agent to one
        or many other Agents. It may contain arbitrary data and trigger
        a specific event on reception.
    """

    def __init__(self, origin: str, event: str, *args):
        self._origin = origin
        self._event = event
        self._data = args
        self._date = None
        self._nonce = 0
        self._recipient = None

    @property
    def origin(self) -> str:
        """
            Get the origin of the message
        """
        return self._origin

    @property
    def event(self) -> str:
        """
            Get the event that should be fired on reception of the Message
        """
        return self._event

    @property
    def data(self) -> tuple:
        """
            Get the data contained in the Message
        """
        return self._data

    @property
    def date(self) -> int:
        """
            Get the date at which the message should be received
        """
        return self._date

    @property
    def nonce(self) -> int:
        """
            Get the nonce of the message
        """
        return self._nonce

    @nonce.setter
    def nonce(self, value: int):
        self._nonce = value

    @property
    def recipient(self) -> str:
        """
            Get the recipient of the message
        """
        return self._recipient

    @recipient.setter
    def recipient(self, recipient: str):
        self._recipient = recipient

    @date.setter
    def date(self, date: int):
        self._date = date

    def __lt__(self, other: 'Message') -> bool:
        if self._date == other.date:
            return self._nonce < other.nonce

        return self._date < other.date


class RunSchedulable(Message):
    """
        Message sent when a agent whishes to schedule the execution of one
        of its behavior at a later point in time.
    """

    def __init__(self, origin: str, schedulable: str):
        _event = RUN_SCHEDULABLE
        super().__init__(origin, _event, schedulable)


class RequestBootstrapPeers(Message):

    """
        Message sent when an Agent whishes to get a list of bootstraping
        peer nodes in the Network.
    """

    def __init__(self, origin: str):
        _event = REQUEST_BOOTSTRAP_PEERS
        super().__init__(origin, _event, origin)


class RequestBootstrapStaticPeers(Message):

    """
        Message sent when an Agent whishes to get the lists of static
        bostraping peer nodes in the network.
    """

    def __init__(self, origin: str):
        _event = REQUEST_BOOTSTRAP_STATIC_PEERS
        super().__init__(origin, _event, origin)


class BootStrapPeers(Message):

    """
        Message sent to agents to give them the list of bootstraping nodes
    """

    def __init__(self, origin: str, bootstrap_list: list[str]):
        _event = BOOTSTRAP_PEERS
        super().__init__(origin, _event, bootstrap_list)


class BootStrapStaticPeers(Message):

    """
        Message sent to agents to give them the static list of bootstraping nodes
    """

    def __init__(self, origin: str, inbound_bootsrap_list: list[str], outbound_bootstrap_list: list[str]):
        _event = BOOTSTRAP_STATIC_PEERS
        super().__init__(origin, _event, inbound_bootsrap_list, outbound_bootstrap_list)


class RequestPeerDiscovery(Message):

    """
        Message sent to other agents to request peer discovery
    """

    def __init__(self, origin: str):
        _event = REQUEST_PEER_DISCOVERY
        super().__init__(origin, _event, origin)


class PeerDiscovery(Message):

    """
        Message sent to an agent that previously requested peer discovery
    """

    def __init__(self, origin: str, peers: list[str]):
        _event = PEER_DISCOVERY
        super().__init__(origin, _event, peers)


class RequestInboundPeer(Message):

    """
        Message sent when an Agent (1) whishes to connect
        to another Agent (2).

        (1) states its intention to become and inbound peer of (2)
    """

    def __init__(self, origin: str):
        _event = REQUEST_INBOUND_PEER
        super().__init__(origin, _event, origin)


class AcceptInboundPeer(Message):

    """
        Message sent when an Agent (1) accepts the connection
        request from another Agent (2)
    """

    def __init__(self, origin: str):
        _event = ACCEPT_INBOUND_PEER
        super().__init__(origin, _event, origin)


class DenyInboundPeer(Message):

    """
        Message sent when an Agent (1) denies the connection
        request from another Agent (2)
    """

    def __init__(self, origin: str):
        _event = DENY_INBOUND_PEER
        super().__init__(origin, _event, origin)


class DropInboundPeer(Message):

    """
        Message sent when an Agent (1) notifies another Agent (2)
        that the connection between them will no longer be maintained
        by (1)
    """

    def __init__(self, origin: str):
        _event = DROP_INBOUND_PEER
        super().__init__(origin, _event, origin)


class StopSimulation(Message):

    """
        Message sent to notify an Agent that the Simulation
        should come to an end.
    """

    def __init__(self, origin: str):
        _event = STOP_SIMULATION
        super().__init__(origin, _event)


class NextSlot(Message):

    """
        Message sent to notify an Agent to move on to the next time slot.
    """

    def __init__(self, origin: str, slot: int, attesters: list[str]):
        _event = NEXT_SLOT
        super().__init__(origin, _event, slot, attesters)


class NextEpoch(Message):

    """
        Message sent to notify an Agent to move on the the next time epoch
    """

    def __init__(self, origin: str, epoch: int):
        _event = NEXT_EPOCH
        super().__init__(origin, _event, epoch)


class CreateBlock(Message):

    """
        System Message sent to notify an agent that it can create
        a Block.
    """

    def __init__(self, origin: str):
        _event = CREATE_BLOCK
        super().__init__(origin, _event)


class ProposeBlockHeader(Message):

    """
        Message sent to propose a newly created block header to other participants
    """

    def __init__(self, origin: str, header: IBlockHeader):
        _event = RECEIVE_BLOCK_HEADER
        super().__init__(origin, _event, header.from_serialized(header.serialize))


class ProposeBlock(Message):

    """
        Message sent to propose a newly created block to other participants.
    """

    def __init__(self, origin: str, block: 'Block'):
        _event = RECEIVE_BLOCK
        super().__init__(origin, _event, block.from_serialized(block.serialize()))


class RequestBlock(Message):

    """ 
        Message sent to request a specific block to one or several peer
    """

    def __init__(self, origin: str, hash: str):
        _event = REQUEST_BLOCK
        super().__init__(origin, _event, hash)


class DiffuseBlock(Message):

    """
        Message sent to diffuse a block to the network
    """

    def __init__(self, origin: str, block: 'Block'):
        _event = RECEIVE_BLOCK
        super().__init__(origin, _event, block.from_serialized(block.serialize()))


class CreateTransaction(Message):

    """
        System Message sent to notify an agent that it can create
        a Transaction.
    """

    def __init__(self, origin: str, fee: int, amount: int, payload: int, receiver: int):
        _event = CREATE_TRANSACTION
        super().__init__(origin, _event, fee, amount, payload, receiver)


class DiffuseTransaction(Message):

    """
        Message sent to diffuse a transaction to the network
    """

    def __init__(self, origin: str, tx: 'Transaction'):
        _event = RECEIVE_TRANSACTION
        super().__init__(origin, _event, tx.from_serialized(tx.serialize()))

class RequestBlockEndorsement(Message):
    """
        Message sent to request a block endorsement to one or several peer
    """
    def __init__(self, origin: str):
        _event = REQUEST_BLOCK_ENDORSEMENT
        super().__init__(origin, _event)

class DiffuseBlockEndorsement(Message):

    """
        Message sent to diffuse a block endorsement to the network
    """

    def __init__(self, origin: str, endorsement: 'Serializable'):
        _event = RECEIVE_BLOCK_ENDORSEMENT
        super().__init__(origin, _event, endorsement.from_serialized(endorsement.serialize()))
