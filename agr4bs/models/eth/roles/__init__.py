"""
    Wrapper module over the different Roles exising in AGR4BS.
"""
from .block_endorser import BlockEndorser
from .block_proposer import BlockProposer
from .blockchain_maintainer import BlockchainMaintainer
from .contractor import Contractor
from .group_manager import GroupManager
from .investee import Investee
from .investor import Investor
from .oracle import Oracle
from .transaction_endorser import TransactionEndorser
from .transaction_proposer import TransactionProposer
from .block_creator_elector import BlockCreatorElector
from .transaction_creator_elector import TransactionCreatorElector
