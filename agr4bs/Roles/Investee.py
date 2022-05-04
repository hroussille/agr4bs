from ..Role import Role, RoleType
from ..Common import Investment
from ..Agent import Agent


class Investee(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTEE)
        self._investors = {}

    def receive(self, agent: Agent, investment: Investment, *args, **kwargs):
        """ Receive an investment from an Investor

            :param agent: the agent to redistribute to
            :type agent: Agent
            :param investment: the investment description
            :type investment: Investment
        """
        raise NotImplementedError

    def redistribute(self, agent: Agent, *args, **kwargs) -> bool:
        """ Redistribute earnings to a specific investor as investment

            :param agent: the agent to redistribute to
            :type agent: Agent
            :returns: wether redistribution was successfull or not
            :rtype: bool
        """
        raise NotImplementedError

    def redistributeFull(self, agent: Agent, *args, **kwargs) -> bool:
        """ Redistribute earnings AND investment(s) to a specific investor

            :param agent: the agent to redistribute to
            :type agent: Agent
            :returns: wether the redistribution was successfull or not
            :rtype: bool
        """
        raise NotImplementedError

    def redistributeAll(self):
        """ Redistribute earnings to all investors """
        for investor in self._investors:
            self.redistribute(investor)

    def redistributeFullAll(self):
        """ Redistribute earnings AND investments(s) to all investors"""
        for investor in self._investors:
            self.redistributeFull(investor)
