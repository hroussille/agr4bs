"""
    Transaction file class implementation
"""

import hashlib
import pickle

from ....blockchain import ITransaction, Payload

class Transaction(ITransaction):

    """
        Transaction class implementation :

        A Transaction is essentially a transfer from one Agent to another.
        it may be used to send currency, or to trigger arbitrary logic if
        it targets a smart contract Agent.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, origin: str, to: str, nonce: int, fee: int = 0,  value: int = 0, payload: Payload = None) -> None:
        super().__init__(origin, to, nonce, fee, value, payload)
