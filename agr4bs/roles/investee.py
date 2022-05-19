"""
Abstract implementation of the Investee role as per AGR4BS

InvesteeContextChange:

The InvesteeContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

Investee:

The Investee implementation which MUST contain the following behaviors :
- receive_investment
- redistribute
- redistribute_full
"""

from .role import Role, RoleType
from ..common import Investment
from ..agents import Agent, ContextChange, AgentType


class InvesteeContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (Investee) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.investors = {}


class Investee(Role):

    """
        Implementation of the Investee Role which must
        expose the following behaviors :
        - receive_investment
        - redistribute
        - redistribute_full

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTEE, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required when mounting / unmounting the Role
        """
        return InvesteeContextChange()

    @staticmethod
    def receive_investment(agent: Agent, investment: Investment, *args, **kwargs):
        """ Receive an investment from an Investor

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param investment: the investment description
            :type investment: Investment
        """
        raise NotImplementedError

    @staticmethod
    def redistribute(agent: Agent, investor: Agent, *args, **kwargs) -> bool:
        """ Redistribute earnings to a specific investor as investment

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param investor: the investor to redistribute to
            :type investor: Agent
            :returns: wether redistribution was successfull or not
            :rtype: bool
        """
        raise NotImplementedError

    @staticmethod
    def redistribute_full(agent: Agent, investor: Agent, *args, **kwargs) -> bool:
        """ Redistribute earnings AND investment(s) to a specific investor

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param investor: the investor to redistribute to
            :type investor: Agent
            :returns: wether the redistribution was successfull or not
            :rtype: bool
        """
        raise NotImplementedError
