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
        self._last_run_time = 0

    @property
    def handler(self):
        """
            Get the handler (i.e., the behavior) contained in the
            Schedulable
        """
        return self._handler

    def should_run(self, time) -> bool:
        """
            Get a boolean indicator on wether or not the Schedulable
            should be run now or not.
        """
        return time - self._last_run_time >= self._frequency

    def update(self, time):
        """
            Update the Schedulable last run time
        """
        self._last_run_time = time

    def __eq__(self, __o: object) -> bool:
        return __o == self._handler
