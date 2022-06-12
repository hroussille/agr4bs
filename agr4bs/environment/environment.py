"""
    Environment file class implementation
"""

import asyncio
import signal
import random

from ..network.messages import StopSimulation
from ..agents import ExternalAgent
from ..factory import Factory

SIGNAL_FLAG = False
EXCEPTION_FLAG = False


# pylint: disable=unused-argument
def signal_handler(*args):
    """
        Global signal handler for OS signals
    """

    # pylint: disable=global-statement
    global SIGNAL_FLAG
    SIGNAL_FLAG = True

    print("Received kill signal !")
    print("Stopping simulation...")


class Environment(ExternalAgent):

    """
        Environment class implementation :

        The Environment manages Groups, Agents and the Network
        to form a complete simulation.
    """

    def __init__(self, factory: Factory = None):
        super().__init__("environment", None, factory)
        self._agents = {}
        self._network.register_agent(self)
        self._agent_tasks = []
        self._running = False

    @property
    def agents_names(self):
        """
            Get the list of agent names
        """
        return list(self._agents.keys())

    @property
    def running(self):
        """
            Get the indicator about the running status of the environment.
        """
        return self._running

    def add_agent(self, agent: ExternalAgent):
        """ Add an Agent to the Environment

            :param agent: the Agent to add to the Environment
            :type agent: Agent
            :raises ValueError: If an agent is added twice to the Environment
        """
        if self.has_agent_by_name(agent.name):
            raise ValueError(
                "Attempting to add an already existing agent to the environment")

        self._agents[agent.name] = agent
        self._network.register_agent(agent)

        if self._running is True:
            self._run_agent(agent)

    async def remove_agent(self, agent: ExternalAgent):
        """ Remove an Agent from the Environment

            :param agent: the Agent to remove from the Environment
            :type agent: Agent
            :raises ValueError: If the agent is not present in the Environment.
        """
        if self.has_agent_by_name(agent.name) is False:
            raise ValueError(
                "Attempting to remove a non existing agent from the environment")

        await self._network.flush_agent(agent)
        del self._agents[agent.name]

    def has_agent(self, agent: ExternalAgent) -> bool:
        """ Check if an agent is part of the Environment

            :param agent: the Agent to check for
            :type agent: Agent
        """
        return self.has_agent_by_name(agent.name)

    def has_agent_by_name(self, agent_name: str) -> bool:
        """ Check if an agent is part of the Environment

            :param agent_name: the name of the Agent to check for
            :type agent_name: str
        """
        return agent_name in self._agents

    def get_agent(self, agent: ExternalAgent) -> ExternalAgent:
        """ Get a specific agent from the Environment

            :param agent: the Agent to retrieve
            :type agent: Agent
        """
        return self.get_agent_by_name(agent.name)

    def get_agent_by_name(self, agent_name: str) -> ExternalAgent:
        """ Get a specific agent from the Environment

            :param agent_name: the Agent to retrieve
            :type agent_name: str
        """
        if self.has_agent_by_name(agent_name) is False:
            return None

        return self._agents[agent_name]

    def generate_bootstrap_list(self, agent_name: str):
        """
            Generate a peer bootstrap list for a specific agent
        """
        return [name for name in self._agents if name != agent_name]

    async def stop(self):
        """
            Set the stop flag leading to the termination of the simulation
        """
        self._exit = True

    async def _notify_stop_simulation(self):
        """
            Notify every agent that the simulation should stop.
            This is done through system messages.
        """

        message = StopSimulation(self._name)
        to = list(self._agents.keys())
        await self._network.send_system_message(message, to)

    def _run_agent(self, agent):
        self._agent_tasks.append(asyncio.create_task(agent.run()))

    async def _wait_agent_tasks(self):
        await asyncio.gather(*self._agent_tasks)

    @staticmethod
    async def _wait_message_tasks():
        message_tasks = [task for task in asyncio.all_tasks(
        ) if task.get_name() == "message_delivery"]
        await asyncio.gather(*message_tasks)

    async def run(self):

        """
            Run the main logic of the environment :

            - bind OS signals
            - Bootstrap agents peers
            - Run main loop
            - notify stop simulation
            - cleanup agent tasks
            - cleanup message tasks
        """

        self._running = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        agents = list(self._agents.values())
        random.shuffle(agents)

        for agent in agents:
            self._run_agent(agent)

        await self._init_schedulables()

        while not self._exit and not SIGNAL_FLAG:

            message = await self._get_next_message()
            if message is not None:
                await self._handle_message(message)

            await self._run_schedulables()
            await asyncio.sleep(0)

        await self._notify_stop_simulation()
        await self._wait_agent_tasks()
        await self._wait_message_tasks()

        self._running = False
