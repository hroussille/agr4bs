from ..Role import Role, RoleType
from ..Common import Investment
from ..Agent import Agent, StateChange


class InvesteeStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        self.investors = {}


class Investee(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTEE)

    @staticmethod
    def stateChange() -> StateChange:
        return InvesteeStateChange()

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
