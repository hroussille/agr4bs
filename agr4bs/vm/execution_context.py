"""
    ExecutionContext file class implementation
"""

from ..blockchain import Transaction
from ..state import State


class ExecutionContext:

    def __init__(self, origin: str, _from: str, value: int, depth: int, state: State, vm: 'VM') -> None:
        self._origin = origin
        self._from = _from
        self._value = value
        self._depth = depth
        self._state = state
        self._vm = vm
        self._changes = []

    @property
    def origin(self):
        return self._origin

    @property
    def caller(self):
        return self._from

    @property
    def value(self):
        return self._value

    @property
    def depth(self):
        return self._depth

    @property
    def state(self):
        return self._state

    @property
    def vm(self):
        return self._vm

    @property
    def changes(self):
        return self._changes
