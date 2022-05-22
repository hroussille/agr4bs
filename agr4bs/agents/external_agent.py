"""
    ExternalAgent file class implementation
"""

import asyncio

from collections import defaultdict
from typing import Union

from agr4bs.events.events import STOP_SIMULATION, UPDATE_PEERS
from ..network import Message, MessageType
from .agent import Agent, AgentType
from ..blockchain import Block
from ..factory import Factory


class ExternalAgent(Agent):

    """
        ExternalAgent class implementation :

        An ExternalAgent is a participant in the Blockchain (i.e., EOA).
        It may contribute to the system or simply interact with it autonomously.
    """

    def __init__(self, name: str, genesis: Block, factory: Factory = None):

        super().__init__(name, AgentType.EXTERNAL_AGENT)

        if factory is None:
            factory = Factory()

        self.safe_inject('genesis', genesis)
        self.safe_inject('factory', factory)

        self.drop_time = 0.5
        self.max_inbound_peers = 10
        self.max_outbound_peers = 4

        self._network = factory.build_network()
        self._message_queue = asyncio.Queue()
        self._event_handlers = defaultdict(list)
        self._exit = False

        self._add_event_handler(STOP_SIMULATION, self.stop_simulation_handler)

    @property
    def message_queue(self):
        """
            Get the agent dedicated message queue
        """
        return self._message_queue

    def add_role(self, role: 'Role') -> bool:
        super().add_role(role)

        for _, implementation in role.behaviors.items():

            if hasattr(implementation, 'on'):
                self._add_event_handler(implementation.on, implementation)

    def remove_role(self, role: 'Role') -> bool:
        super().remove_role(role)

        for _, implementation in role.behaviors.items():

            if hasattr(implementation, 'on'):
                self._remove_event_handler(implementation.on, implementation)

    def _add_event_handler(self, event, handler):

        if handler not in self._event_handlers[event]:
            self._event_handlers[event].append(handler)

    def _remove_event_handler(self, event, handler):
        self._event_handlers[event].remove(handler)

    async def stop_simulation_handler(self):
        """
            Core event handler : STOP_SIMULATION
            Sets the agent exit_flag leading to its termination.
        """
        self._exit = True

    async def fire_event(self, event, *args, **kwargs):
        """
            Fire a specific event and wait for the handler(s) to finish
        """
        if event in self._event_handlers:
            for event_handler in self._event_handlers[event]:
                await event_handler(self, *args, **kwargs)

    async def send_message(self, message: Message, to: Union[str, list[str]]):
        """
            Send a Message to one or many agents
        """
        if not isinstance(to, list):
            to = [to]

        await self._network.send_message(message, to)

    async def send_system_message(self, message: Message, to: Union[str, list[str]]):
        """
            Send a Message to one or many agents
        """
        if not isinstance(to, list):
            to = [to]

        await self._network.send_message(message, to)

    async def _get_next_message(self):
        """
            Get the next Message from the message queue
        """
        try:
            message = self._message_queue.get_nowait()
        except asyncio.QueueEmpty:
            message = None

        return message

    async def _handle_message(self, message: Message):
        """
            handle messages and fire the event the message is bound to
        """
        if message.type == MessageType.STOP_SIMULATION:
            self._exit = True

        else:
            await self.fire_event(message.event, *message.data)

    async def run(self):
        """
            Run the agent :
            - handle messages
            - handle schedules events
        """
        while not self._exit:

            message = await self._get_next_message()

            if message is not None:
                await self._handle_message(message)

            await self.fire_event(UPDATE_PEERS)

            # TODO: Fire scheduled events

            await asyncio.sleep(0)
