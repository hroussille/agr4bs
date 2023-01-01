"""
    Wrapper module over the different Roles exising in AGR4BS.
"""
from .role import Role, RoleType
from .peer import Peer
from .static_peer import StaticPeer
from .bootstrap import Bootstrap
from .static_bootstrap import StaticBootstrap
from .block_creator_elector import BlockCreatorElector
from .transaction_creator_elector import TransactionCreatorElector
