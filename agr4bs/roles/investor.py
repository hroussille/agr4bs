"""
Abstract implementation of the Investor role as per AGR4BS

InvestorContextChange:

The InvestorContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

Investor:

The Investor implementation which MUST contain the following behaviors :
- specify_investment
- invest
- withdraw

"""

from .role import Role, RoleType
from ..agents import Agent, ContextChange, AgentType
from ..common import Investment, export


class InvestorContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (Investor) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.investment_strategy = None


class Investor(Role):
    """
       Implementation of the Investor Role which must
        expose the following behaviors :
        - specify_investment
        - invest
        - withdraw

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTOR, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required when mounting / unmounting the Role
        """
        return InvestorContextChange()

    @staticmethod
    @export
    def specify_investment(agent: Agent, *args, **kwargs) -> Investment:
        """ Specify an investment according to the current investment policy

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :returns: the Investment definition
            :rtype: Investment
        """
        raise NotImplementedError

    @staticmethod
    @export
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
    @export
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
