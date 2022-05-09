import hashlib
from .Transaction import Transaction
from ..Agent import Agent


class Block(object):

    def __init__(self, parentHash: str, creator: str, transactions: list[Transaction]) -> None:
        self._parentHash = parentHash
        self._transactions = transactions
        self._creator = creator
        self._hash = self.computeHash()
        self._totalFees = sum(map(lambda tx: tx.fee, self._transactions))
        self._height = 0

    @property
    def parentHash(self) -> "str":
        return self._parentHash

    @property
    def transactions(self) -> list[Transaction]:
        return self._transactions

    @property
    def creator(self) -> Agent:
        return self._creator

    @property
    def totalFees(self) -> int:
        return self._totalFees

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, newHeight: int) -> None:

        if newHeight < 0:
            raise ValueError("Block height cannot be negative")

        self._height = newHeight

    def __str__(self) -> str:
        return self.serialize()

    def serialize(self) -> str:
        serializedTx = ''.join("%s" % ','.join(map(str, self._transactions)))
        return "{{ parentHash: {} - creator: {} - transactions: {} }}".format(self._parentHash, self._creator, serializedTx)

    def computeHash(self) -> str:
        return hashlib.sha256(self.serialize().encode()).hexdigest()
