"""
    Network file class implementation
"""

import queue
import random
import datetime

from agr4bs.network.messages import Message
from ..agents.agent import AgentType


class Network():

    """
        AioNetwork class implementation :

        Simulates a network, where messages can be sent (broadcast)
        with a configurable delay and message drop probability.
    """

    def __init__(self, delay: int = 0, drop_rate: float = 0):
        self._delay = delay
        self._drop_rate = drop_rate
        self._message_count = 0
        self._message_queue = queue.PriorityQueue()

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

    def send_system_message(self, message: Message) -> None:
        """
            Send a system message to the network.
            System messages are not subject to delay or drops.
        """
        message.nonce = self._message_count
        self._message_count = self._message_count + 1
        self._message_queue.put(message)

    def send_message(self, message: Message, no_drop=False) -> None:
        """
            Send a message to the network.
        """
        drop_probability = random.random()

        if drop_probability > self.drop_rate or no_drop is True:
            delta = datetime.timedelta(
                milliseconds=int(random.random() * self.delay))
            message.date = message.date + delta
            message.nonce = self._message_count
            self._message_count = self._message_count + 1
            self._message_queue.put(message)

    def has_message(self):
        """
            Check if the network has a message to deliver
        """
        return not self._message_queue.empty()

    def get_next_message(self):
        """
            Pop and return the next message from the message priority queue
        """
        return self._message_queue.get()

    def flush_agent(self, agent: 'ExternalAgent') -> None:
        """ Flush an ExternalAgent out of the Network

        :param agent: The ExternalAgent to flush out
        :type agent: ExternalAgent
        """

    def register_agent(self, agent: 'ExternalAgent') -> None:
        """
            Register an ExternalAgent in the Network.

            :param agent: The agent to register
            :type agent: ExternalAgent
        """
        if agent.type != AgentType.EXTERNAL_AGENT:
            raise ValueError("Network only allow EXTERNAL_AGENT")
