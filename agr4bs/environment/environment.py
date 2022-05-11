"""
    Environment file class implementation
"""

from ..agent import Agent
from ..network import Network


class Environment():

    """
        Environment class implementation :

        The Environment manages Groups, Agents and the Network
        to form a complete simulation.
    """

    def __init__(self, network: Network = None, initial_state: dict = None) -> None:

        if initial_state is None:
            initial_state = {}

        if network is None:
            network = Network()

        self._network = network
        self._agents = {}
        self.set_initial_state(initial_state)

    def set_initial_state(self, initial_state: dict):
        """ Set the initial state (i.e., genesis state) of the Environment

            :param initial_state: the initial_state to set to the Environment
            :type initial_state: dict
        """
        self._initial_state = initial_state

    def add_agent(self, agent: Agent):
        """ Add an Agent to the Environment

            :param agent: the Agent to add to the Environment
            :type agent: Agent
            :raises ValueError: If an agent is added twice to the Environment
        """
        if self.has_agent_by_name(agent.name):
            raise ValueError(
                "Attempting to add an already existing agent from the environment")

        self._agents[agent.name] = agent

    def remove_agent(self, agent: Agent):
        """ Remove an Agent from the Environment

            :param agent: the Agent to remove from the Environment
            :type agent: Agent
            :raises ValueError: If the agent is not present in the Environment.
        """
        if self.has_agent_by_name(agent.name) is False:
            raise ValueError(
                "Attempting to remove a non existing agent from the environment")

        self._network.flush_agent(agent)
        del self._agents[agent.name]

    def has_agent(self, agent: Agent) -> bool:
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

    def get_agent(self, agent: Agent) -> Agent:
        """ Get a specific agent from the Environment

            :param agent: the Agent to retrieve
            :type agent: Agent
        """
        return self.get_agent_by_name(agent.name)

    def get_agent_by_name(self, agent_name: str) -> Agent:
        """ Get a specific agent from the Environment

            :param agent_name: the Agent to retrieve
            :type agent_name: str
        """
        if self.has_agent_by_name(agent_name) is False:
            return None

        return self._agents[agent_name]
