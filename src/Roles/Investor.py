from Role import Role, RoleType
from Agent import Agent
from src.Common.Investment import Investment


class Investor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTOR)

    def specifyInvestment(self, *args, **kwargs) -> Investment:
        """ Specify an investment according to the current investment policy

            :returns: the Investment definition
            :rtype: Investment
        """
        raise NotImplementedError

    def invest(self, agent: Agent, investment: Investment, *args, **kwargs) -> bool:
        """ Invest in a specific Agent

            :param agent: the agent to invest in
            :type agent: Agent
            :param investment: the investment definition
            :type investment: Investment
            :returns: wether the investment was successfull or not
            :rtype: bool
        """
        raise NotImplementedError

    def withdraw(self, agent: Agent, *args, **kwargs) -> bool:
        """ Withdraw investments from a specific agent

            :param agent: the agent to withdraw from
            :type agent: Agent
            :returns: wether withdrawal request was successfull or not
            :rtype: bool
        """
        raise NotImplementedError
