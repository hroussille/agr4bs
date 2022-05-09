from ..Role import Role, RoleType
from ..Agent import Agent, StateChange
from ..Common import Investment


class InvestorStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        self.investment_strategy = None


class Investor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTOR)

    @staticmethod
    def stateChange() -> StateChange:
        return InvestorStateChange()

    @staticmethod
    def specify_investment(agent: Agent, *args, **kwargs) -> Investment:
        """ Specify an investment according to the current investment policy

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :returns: the Investment definition
            :rtype: Investment
        """
        raise NotImplementedError

    @staticmethod
    def invest(agent: Agent, investee: Agent, investment: Investment, *args, **kwargs) -> bool:
        """ Invest in a specific Agent

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param investee: the agent to invest in
            :type investee: Agent
            :param investment: the investment definition
            :type investment: Investment
            :returns: wether the investment was successfull or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def withdraw(agent: Agent, investee: Agent, *args, **kwargs) -> bool:
        """ Withdraw investments from a specific agent

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param investee: the agent to withdraw from
            :type investee: Agent
            :returns: wether withdrawal request was successfull or not
            :rtype: bool
        """
        raise NotImplementedError
