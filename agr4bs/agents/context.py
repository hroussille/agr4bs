"""
    Context file class implementation
"""

import inspect
from .context_change import ContextChange


class Context():

    """
        Context changes that need to be made to the Agent when
        the associated Role is either
        mounted or unmounted.
    """

    def __init__(self):
        self._context = {}

    def __getitem__(self, key):
        return self._context[key]

    def __iter__(self):
        for entry in self._context:
            yield entry

    def __setitem__(self, key, value):
        self._context[key] = value

    @staticmethod
    def _is_init_function(reference) -> bool:

        if callable(reference) is False:
            return False

        sig = inspect.signature(reference)

        if len(sig.parameters) < 1:
            return False

        if list(sig.parameters.items())[0][0] != "context":
            return False

        return True

    def apply_context_change(self, context_change: ContextChange) -> None:
        """
            Apply all the changes described in Context_change

            :param Context_change: the changes that need to be reverted from the Context
            :type Context_change: ContextChange
        """
        for key, value in context_change.mount().items():

            if key not in self._context:

                if self._is_init_function(value):
                    self._context[key] = value(self)

                else:
                    self._context[key] = value

    def revert_context_change(self, context_change: ContextChange) -> None:
        """
            Revert all the changes described in Context_change

            :param Context_change: the changes that need to be made to the Context
            :type Context_change: ContextChange
        """

        for key in context_change.unmount():
            del self._context[key]
