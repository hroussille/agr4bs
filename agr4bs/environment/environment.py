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

        self.network = network
        self.agents = {}
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
        if self.agents[agent.name] is not None:
            raise ValueError(
                "Attempting to add an already existing agent from the environment")

        self.agents[agent.name] = agent

    def remove_agent(self, agent: Agent):
        """ Remove an Agent from the Environment

            :param agent: the Agent to remove from the Environment
            :type agent: Agent
            :raises ValueError: If the agent is not present in the Environment.
        """
        if self.agents[agent.name] is None:
            raise ValueError(
                "Attempting to remove a non existing agent from the environment")

        self.network.flush_agent(agent)
        del self.agents[agent.name]
