from typing import DefaultDict
from agr4bs.agents.internal_agent import InternalAgentResponse, Revert, Success
from ...roles import Role, RoleType
from ...agents import InternalAgent, AgentType
from ...common import export

class ERC20(Role):

    """
        Implementation of the ERC-20 Role managing fungible tokens.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(agent: InternalAgent, name: str, symbol: str) -> InternalAgentResponse:

        """
             Constructor of the ERC20 implementation
            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param name: the name of the implemented token (i.e., : WErapped Ethereum)
            :type name: str
            :param symbol: the symbol of the implemented token (i.e., WETTH)
            :type symbol: str
            :returns: Success Response
            :rtype: Success
            
        """
        agent.set_storage_at("name", name)
        agent.set_storage_at("symbol", symbol)
        agent.set_storage_at("balances", DefaultDict(lambda: 0))
        agent.set_storage_at("allowances", DefaultDict(lambda: DefaultDict(lambda: 0)))
        return Success()
    
    @staticmethod
    @export
    def decimals(agent: InternalAgent) -> InternalAgentResponse:

        """
            Decimals getter

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :returns: response
            :rtype: InternalAgentResponse
        """
        return Success(decimals=18)

    @staticmethod
    @export
    def balance_of(agent: InternalAgent, name: str) -> InternalAgentResponse:
        """
            Account balance getter

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param name: the name of the agent to get the balance for
            :type name: str
            :returns: Success Response
            :rtype: Success
        """
        balances: dict = agent.get_storage_at("balances")
        return Success(balance=balances[name])
    
    @staticmethod
    @export
    def transfer(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:
        """
            Transfer some amount to another agent]

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param to: the name of the agent to transfer to
            :type to: str
            :param amount: the amount to transfer
            :type amount: int
            :returns: response
            :rtype: InternalAgentResponse
            
        """
        balances: dict = agent.get_storage_at("balances")
        caller: str = agent.caller()

        if balances[caller] < amount:
            return Revert("ERC20 : Not enough balance")

        balances[caller] -= amount
        balances[to] += amount

        return Success()

    @staticmethod
    @export
    def transfer_from(agent: InternalAgent, _from: str, to: str, amount: int) -> InternalAgentResponse:

        """
        Transfer some amount to another agent]

        :param agent: the agent on which the behavior operates
        :type agent: Agent
        :param to: the name of the agent to transfer to
        :type to: str
        :param amount: the amount to transfer
        :type amount: int
        :returns: response
        :rtype: InternalAgentResponse
        """

        allowances: dict = agent.get_storage_at("allowances")
        balances: dict = agent.get_storage_at("balances")
        caller : str = agent.caller()

        if allowances[_from][caller] < amount:
            return Revert("ERC20 : Insufficient allowance")

        allowances[_from][caller] -= min(allowances[_from][caller], amount)
        
        if balances[_from] < amount:
            return Revert("ERC20 : Not enough balance")

        balances[_from] -= amount
        balances[to] += amount

        return Success()

    @staticmethod
    @export
    def increase_allowance(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:

        """
        Transfer some amount to another agent]

        :param agent: the agent on which the behavior operates
        :type agent: Agent
        :param to: the name of the agent to increase allowance for
        :type to: str
        :param amount: the amount of additional allowance
        :type amount: int
        :returns: response
        :rtype: InternalAgentResponse
        """

        allowances: dict = agent.get_storage_at("allowances")
        caller: str = agent.caller()

        allowances[caller][to] += amount

        return Success()

    @staticmethod
    @export
    def decrease_allowance(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:

        """
        Transfer some amount to another agent]

        :param agent: the agent on which the behavior operates
        :type agent: Agent
        :param to: the name of the agent to decrease allowance for
        :type to: str
        :param amount: the amount of allowance to remove
        :type amount: int
        :returns: response
        :rtype: InternalAgentResponse
        """

        allowances: dict = agent.get_storage_at("allowances")
        caller: str = agent.caller()

        allowances[caller][to] -= min(allowances[caller][to], amount)

        return Success()