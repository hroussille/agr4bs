"""
    Network file class implementation
"""

import asyncio
import random

from agr4bs.network.messages import Message
from ..agents.agent import AgentType


class AioNetwork():

    """
        AioNetwork class implementation :

        Simulates a network, where messages can be sent (broadcast)
        with a configurable delay and message drop probability.
    """

    def __init__(self, delay: float = 0, drop_rate: float = 0):
        self._delay = delay
        self._drop_rate = drop_rate
        self._queues = {}

    @property
    def delay(self):
        """
            Get the average network delay
        """
        return self._delay

    @property
    def drop_rate(self):
        """
            Get the average message drop rate
        """
        return self._drop_rate

    @staticmethod
    async def _deliver_message(queue: asyncio.Queue, message: Message, delay: float):
        """
            Deliver a given message to a given Queue by applying a simulated network delay
        """
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            queue.put_nowait(message)

        except asyncio.QueueFull:
            print("Overloaded message queue")

    async def send_system_message(self, message: Message, to: list[str]) -> None:
        """
            Send a system message to the network.

            System messages are not subject to delay or drops.
        """
        delivery_tasks = []

        for recipient in to:
            if recipient in self._queues:
                queue = self._queues[recipient]
                delivery_tasks.append(self._deliver_message(queue, message, 0))

        await asyncio.gather(*delivery_tasks)

    async def send_message(self, message: Message, to: list[str]) -> None:
        """
            Send a message to the network.
        """

        for recipient in to:
            if recipient in self._queues:
                if random.random() > self.drop_rate:
                    delay = random.random() * self.delay
                    queue = self._queues[recipient]
                    asyncio.create_task(
                        self._deliver_message(queue, message, delay), name="message_delivery")

    async def flush_agent(self, agent: 'ExternalAgent') -> None:
        """ Flush an ExternalAgent out of the Network

        :param agent: The ExternalAgent to flush out
        :type agent: ExternalAgent
        """
        if agent.name not in self._queues:
            raise ValueError("Flushing non existing agent")

        del self._queues[agent.name]
        # TODO: Send agent disconnected to all agents

    def register_agent(self, agent: 'ExternalAgent') -> None:
        """
            Register an ExternalAgent in the Network.

            :param agent: The agent to register
            :type agent: ExternalAgent
        """
        if agent.type != AgentType.EXTERNAL_AGENT:
            raise ValueError("Network only allow EXTERNAL_AGENT")

        if agent.name in self._queues:
            raise ValueError(
                "Network allow only one registration per ExternalAgent")

        self._queues[agent.name] = agent.message_queue
