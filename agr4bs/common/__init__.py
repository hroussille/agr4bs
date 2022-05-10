"""
    agr4bs common submodule

    This module holds "data structures" necessary to the
    construction of any blockchain such as Transactions and
    Blocks. It also includes a primitive Blockchain implementation.
"""

from .transaction import Transaction
from .block import Block
from .payload import Payload
from .blockchain import Blockchain
from .investment import Investment
