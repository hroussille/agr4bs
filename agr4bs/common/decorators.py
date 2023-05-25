
"""
    Behavior decorators classes implementations
"""

import inspect
import datetime

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


class every:

    """
        The every decorator adds the event names to the `on` property
        of the function is decorates so that the framework can bind
        the execution of the decorated function to the given events.
    """

    def __init__(self, days=0, hours=0, minutes=0, seconds=0, miliseconds=0, microseconds=0):

        self._frequency = datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=miliseconds, microseconds=microseconds)

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


def payable(function):
    """
       The payable decorator adds the payable property to an InternalAgent function
       allowing it to be called with a non zero value
    """
    function.payable = True

    return function


def export(function):
    """
        The export decorator marks a role behavior for exportation. An agent taking the role
        will also take on that behavior.
    """

    function.export = True

    return function
