
"""
    Behavior decorators classes implementations
"""

import inspect

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name


class on:

    """
        The on decorator adds the event names to the `on` property
        of the function is decorates so that the framework can bind
        the execution of the decorated function to the given events.
    """

    def __init__(self, event_name):
        self._event_name = event_name

    def __call__(self, function):

        if hasattr(function, 'on'):
            raise ValueError(
                "Behaviors cannot be bound to more than one event")

        if hasattr(function, 'every'):
            raise ValueError(
                "Behaviors can only be bound to `on` or `every` but not both")

        function.on = self._event_name

        return function


MILISECONDS = 1 / 1000
SECONDS = 1
MINUTES = 60

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name


class every:

    """
        The every decorator adds the event names to the `on` property
        of the function is decorates so that the framework can bind
        the execution of the decorated function to the given events.
    """

    def __init__(self, frequency: int, unit: int):

        if frequency <= 0:
            raise ValueError("Frequency must be greater than 0")

        if unit not in [MILISECONDS, SECONDS, MINUTES]:
            raise ValueError("Uknown frequency parameter")

        self._frequency = frequency * unit

    def __call__(self, function):

        if hasattr(function, 'on'):
            raise ValueError(
                "Behaviors can only be bound to `on` or `every` but not both")

        sig = inspect.signature(function)

        if len(sig.parameters) != 1:
            raise ValueError(
                "Behavior scheduled with @every can only take a single ExternalAgent parameter")

        function.frequency = self._frequency

        return function
