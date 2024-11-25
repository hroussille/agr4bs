from typing import DefaultDict
from .....agents import InternalAgentResponse, Revert, Success
from .....roles import Role, RoleType
from .....agents import InternalAgent, AgentType
from .....common import export


class ERC721(Role):

    """
        Implementation of the ERC-721 Role managing non fungible tokens.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT, [])

    @staticmethod
    @export
    def constructor(agent: InternalAgent, name: str, symbol: str) -> InternalAgentResponse:
        """
             Constructor of the ERC721 implementation
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
        agent.set_storage_at("balances", DefaultDict(
            lambda: DefaultDict(lambda: 0)))
        agent.set_storage_at("allowances", DefaultDict(
            lambda: DefaultDict(lambda: DefaultDict(lambda: 0))))
        return Success()

    @staticmethod
    @export
    def balance_of(agent: InternalAgent, name: str, token_id: int) -> InternalAgentResponse:
        """
            Account balance getter

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param name: the name of the agent to get the balance for
            :type name: str
            :param tokenId: ID of the token to check the balance for
            :type tokenId: int
            :returns: Success Response
            :rtype: Success
        """

        balances: dict = agent.get_storage_at("balances")
        return Success(balance=len(balances[name][token_id]))

    @staticmethod
    @export
    def transfer(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:
        balances: dict = agent.get_storage_at("balances")
        caller: str = agent.caller()

        if balances[caller] < amount:
            return Revert("ERC721 : Not enough balance")

        balances[caller] -= amount
        balances[to] += amount

    @staticmethod
    @export
    def transferFrom(agent: InternalAgent, _from: str, to: str, amount: int) -> InternalAgentResponse:
        allowances: dict = agent.get_storage_at("allowances")
        balances: dict = agent.get_storage_at("balances")
        caller: str = agent.caller()

        if allowances[_from][caller] < amount:
            return Revert("ERC721 : Insufficient allowance")

        allowances[_from][caller] -= min(allowances[_from][caller], amount)

        if balances[_from] < amount:
            return Revert("ERC721 : Not enough balance")

        balances[_from] -= amount
        balances[to] += amount

    @staticmethod
    @export
    def increaseAllowance(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:
        allowances: dict = agent.get_storage_at("allowances")
        caller: str = agent.caller()

        allowances[caller][to] += amount

    @staticmethod
    @export
    def decreaseAllowance(agent: InternalAgent, to: str, amount: int) -> InternalAgentResponse:
        allowances: dict = agent.get_storage_at("allowances")
        caller: str = agent.caller()

        allowances[caller][to] -= min(allowances[caller][to], amount)
