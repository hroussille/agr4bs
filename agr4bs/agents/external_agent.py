"""
    ExternalAgent file class implementation
"""
import copy
import datetime
import pickle

from collections import defaultdict
from typing import Union
from ..events.events import RUN_SCHEDULABLE
from ..network.messages import RunSchedulable
from ..events import INIT, STOP_SIMULATION, RECEIVE_MESSAGE, SEND_MESSAGE, CLEANUP
from ..network import Message
from .agent import Agent, AgentType
from ..blockchain import IBlock
from .schedulable import Schedulable


class ExternalAgent(Agent):

    """
        ExternalAgent class implementation :

        An ExternalAgent is a participant in the Blockchain (i.e., EOA).
        It may contribute to the system or simply interact with it autonomously.
    """

    def __init__(self, name: str, genesis: IBlock, factory: 'IFactory'):

        super().__init__(name, AgentType.EXTERNAL_AGENT)

        self.safe_inject('genesis', genesis)
        self.safe_inject('factory', factory)

        self.drop_time = 2
        self.max_inbound_peers = 15
        self.max_outbound_peers = 5

        self._network = factory.build_network()
        self._event_handlers = defaultdict(list)
        self._schedulables = {}
        self._exit = False
        self._date = None

        self._add_event_handler(STOP_SIMULATION, self.stop_simulation_handler)
        self._add_event_handler(RUN_SCHEDULABLE, self.run_schedulable_handler)

    @property
    def date(self):
        """
            Get the current date from the agent point of vue
        """
        return self._date

    @date.setter
    def date(self, new_date):
        """
            Update the current date for the agent
        """
        self._date = new_date

    def add_role(self, role: 'Role') -> bool:
        super().add_role(role)

        for behavior_name, implementation in role.behaviors.items():

            if hasattr(implementation, 'on'):
                self._add_event_handler(implementation.on, implementation)

            elif hasattr(implementation, 'frequency'):
                frequency = implementation.frequency
                self._add_schedulable(behavior_name, frequency, implementation)

    def remove_role(self, role: 'Role') -> bool:
        super().remove_role(role)

        for behavior_name, implementation in role.behaviors.items():

            if hasattr(implementation, 'on'):
                self._remove_event_handler(implementation.on, implementation)

            elif hasattr(implementation, 'frequency'):
                self._remove_schedulable(behavior_name)

    def _add_event_handler(self, event, handler):

        if handler not in self._event_handlers[event]:
            self._event_handlers[event].append(handler)

    def _remove_event_handler(self, event, handler):
        self._event_handlers[event].remove(handler)

    def _add_schedulable(self, name: str, frequency: int, handler: callable):
        self._schedulables[name] = Schedulable(frequency, handler)

    def _remove_schedulable(self, name):
        if name in self._schedulables:
            del self._schedulables[name]

    @staticmethod
    def stop_simulation_handler(agent: 'ExternalAgent'):
        """
            Core event handler : STOP_SIMULATION
            Sets the agent exit_flag leading to its termination.
        """
        agent._exit = True

    @staticmethod
    def run_schedulable_handler(agent: 'ExternalAgent', behavior_name: str):
        """
            Core event handler : RUN_SCHEDULABLE
            Run a scheduled behavior
        """
        if behavior_name in agent._schedulables:
            schedulable = agent._schedulables[behavior_name]
            schedulable.handler(agent)
            agent.schedule_behavior(behavior_name, schedulable.frequency)

    def fire_event(self, event, *args, **kwargs):
        """
            Fire a specific event and wait for the handler(s) to finish
        """
        if event in self._event_handlers:
            for event_handler in self._event_handlers[event]:
                event_handler(self, *args, **kwargs)

    def send_message(self, message: Message, to: Union[str, list[str]], no_drop=False):
        """
            Send a Message to one or many agents
        """
        if not isinstance(to, list):
            to = [to]

        for recipient in to:
            _message = pickle.loads(pickle.dumps(message, -1))
            _message.recipient = recipient
            _message.date = self._date
            self._network.send_message(_message, no_drop=no_drop)

        self.fire_event(SEND_MESSAGE, to)

    def send_system_message(self, message: Message, to: Union[str, list[str]], delay=None):
        """
            Send a Message to one or many agents
        """
        if not isinstance(to, list):
            to = [to]

        for recipient in to:
            _message = copy.copy(message)
            _message.recipient = recipient
            _message.date = self._date

            if delay is not None:
                _message.date = _message.date + delay

            self._network.send_system_message(_message)

    def handle_message(self, message: Message):
        """
            Handle a given message by firing the associated events
        """
        self.fire_event(RECEIVE_MESSAGE, message.origin)
        self.fire_event(message.event, *message.data)

    def schedule_behavior(self, behavior_name: str, frequency: datetime.timedelta):
        message = RunSchedulable(self.name, behavior_name)
        self.send_system_message(message, self.name, delay=frequency)

    def _init_schedulables(self):
        for behavior_name, schedulable in self._schedulables.items():
            self.schedule_behavior(behavior_name, schedulable.frequency)

    def init(self, date):
        """
            Initializes the agent
        """
        self._date = date
        self._init_schedulables()
        self.fire_event(INIT)

    def cleanup(self):
        """
            Cleanup the agent
        """
        self.fire_event(CLEANUP)
