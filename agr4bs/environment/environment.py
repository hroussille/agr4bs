"""
    Environment file class implementation
"""
import random

from ..network.messages import StopSimulation
from ..agents import ExternalAgent
from ..factory import IFactory


class Environment(ExternalAgent):

    """
        Environment class implementation :

        The Environment manages Groups, Agents and the Network
        to form a complete simulation.
    """

    def __init__(self, factory: IFactory):
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
            agent.init(self._date)

    def remove_agent(self, agent: ExternalAgent):
        """ Remove an Agent from the Environment

            :param agent: the Agent to remove from the Environment
            :type agent: Agent
            :raises ValueError: If the agent is not present in the Environment.
        """
        if self.has_agent_by_name(agent.name) is False:
            raise ValueError(
                "Attempting to remove a non existing agent from the environment")

        self._network.flush_agent(agent)
        agent.cleanup()

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

    def init(self, date):

        super().init(date)

        agents_names = self.agents_names
        random.shuffle(agents_names)

        for agent_name in agents_names:
            self._agents[agent_name].init(date)

    def cleanup(self):
        super().cleanup()

        agents_names = self.agents_names
        random.shuffle(agents_names)

        for agent_name in agents_names:
            self._agents[agent_name].cleanup()

    def stop(self):
        """
            Set the stop flag leading to the termination of the simulation
        """
        self._exit = True

    def _notify_stop_simulation(self):
        """
            Notify every agent that the simulation should stop.
            This is done through system messages.
        """

        message = StopSimulation(self._name)
        to = list(self._agents.keys())
        self.send_system_message(message, to)
