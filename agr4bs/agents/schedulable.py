"""
    Schedulable file class implementation
"""


class Schedulable:

    """
        A Schedulable is a wrapper over a behavior that should
        be run by the agent at a specific frequency.
    """

    def __init__(self, frequency, handler):
        self._frequency = frequency
        self._handler = handler

    @property
    def handler(self):
        """
            Get the handler (i.e., the behavior) contained in the
            Schedulable
        """
        return self._handler

    @property
    def frequency(self):
        """
            Get the frequency as which the associated behavior should be ran
        """
        return self._frequency

    def __eq__(self, __o: object) -> bool:
        return __o == self._handler
