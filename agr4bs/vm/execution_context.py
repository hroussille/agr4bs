"""
    ExecutionContext file class implementation
"""

from ..state import State
import pickle
import copy


class ExecutionContext:

    def __init__(self, origin: str, _from: str, to: str, value: int, depth: int, state: State, vm: 'VM') -> None:
        self._origin = origin
        self._from = _from
        self._to = to
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
    def to(self):
        return self._to

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

    def clear_changes(self):
        self._changes = []

    def merge_changes(self, changes: list):
        self._changes = self._changes + changes

    def copy(self) -> 'ExecutionContext':
        """
            Copy the current ExecutionContext
        """
        return copy.deepcopy(self)
        # pickle.loads(pickle.dumps(self))
