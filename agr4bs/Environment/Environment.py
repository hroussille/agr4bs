from agr4bs.Agent import Agent


class Network(object):
    def __init__(self) -> None:
        pass


class Environment(object):

    def __init__(self, network: Network = None, initial_state: dict = None) -> None:

        if initial_state is None:
            initial_state = {}

        if network is None:
            network = Network()

        self.network = network
        self.agents = {}
        self.set_initial_state(initial_state)

    def set_initial_state(self, initial_state: dict):
        self._initial_state = initial_state

    def add_agent(self, agent: Agent):

        if self.agents[agent.name] is not None:
            raise ValueError(
                "Attempting to add an already existing agent from the environment")

        self.agents[agent.name] = agent

    def remove_agent(self, agent: Agent):

        if self.agents[agent.name] is None:
            raise ValueError(
                "Attempting to remove a non existing agent from the environment")

        self.network.flush_agent(agent)
        del self.agents[agent.name]
