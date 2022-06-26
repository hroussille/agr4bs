"""
    InternalAgent file class implementation
"""

from typing import Callable

from ..common import Serializable
from .agent import Agent, AgentType
import inspect


class InternalAgentCalldata(Serializable):

    """
        InternalAgentCall class implementation :

        An InternalAgentCall is a standard to interact with InternalAgents
        on the Blockchain.
    """

    def __init__(self, function: str, **parameters):
        super().__init__()
        self._function = function
        self._parameters = parameters

    @property
    def function(self):
        """
            Get the function called by this request
        """
        return self._function

    @property
    def parameters(self):
        """
            Get the parameters of this request
        """
        return self._parameters


class InternalAgentDeployement(Serializable):

    """
        InternalAgentDeployement class implementation :

        An InternalAgentDeployement is a standard way to deploy an internalAgent
        on the Blockchain
    """

    def __init__(self, agent: 'InternalAgent', **parameters) -> None:

        super().__init__()
        self._agent = agent
        self._constructor_calldata = InternalAgentCalldata(
            "constructor", **parameters)

    @property
    def agent(self):
        return self._agent

    @property
    def constructor_calldata(self):
        return self._constructor_calldata


class InternalAgentResponse:

    """
        InternalAgentResponse class implementation :

        An InternalAgentResponse is a standard to receive data back from
        an InternalAgent called through an InternalAgentCall.
    """

    def __init__(self, reverted: bool = False, revert_reason: str = None, return_values: dict = None):

        if return_values is None:
            return_values = {}

        self._reverted = reverted
        self._revert_reason = revert_reason
        self._return_value = return_values

    @property
    def reverted(self):
        """
            Get the reverted indicator
        """
        return self._reverted

    @property
    def revert_reason(self):
        """
            Get the revert reason. Only relevant when reverted is True.
        """
        return self._revert_reason

    @property
    def return_value(self):
        """
            Get the return values. Only relevant when reverted is False.
        """
        return self._return_value


class Revert(InternalAgentResponse):

    def __init__(self, revert_reason: str):
        super().__init__(reverted=True, revert_reason=revert_reason, return_values=None)


class Success(InternalAgentResponse):
    def __init__(self, **return_values):
        super().__init__(reverted=False, revert_reason=None, return_values=return_values)


class InternalAgent(Agent):

    """
        InternalAgent class implementation :

        An InternalAgent is a program in the Blockchain (i.e., Smart Contract).
        It may only act in the system when it is triggered by a transaction coming
        from an ExternalAgent.
    """

    def __init__(self, name: str):
        super().__init__(name, AgentType.INTERNAL_AGENT)
        self._constructor_called = False
        self.ctx = None

    def constructor(self):
        """
            Constructor of the InternalAgent inside the blockchain context.
        """

        if self._constructor_called is False:
            self._constructor_called = True
            return Success()

        else:
            return Revert("Constructor already called")

    def validate_call(self, calldata: InternalAgentCalldata, ctx: 'ExecutionContext') -> InternalAgentResponse:

        function_name = calldata.function
        parameters = calldata.parameters
        value = ctx.value

        if self._validate_function(function_name) is False:
            return InternalAgentResponse(reverted=True, revert_reason="Uknown function")

        function = getattr(self, function_name)

        if self._validate_parameters(function, parameters) is False:
            return InternalAgentResponse(reverted=True, revert_reason="Invalid parameters")

        if self._validate_value(function, value) is False:
            return InternalAgentResponse(reverted=True, revert_reason="Function is not payable")

        return None

    def _validate_function(self, function_name: str) -> bool:

        if not self.has_behavior(function_name):
            return False

        if not inspect.ismethod(getattr(self, function_name)):
            return False

        return True

    def _validate_parameters(self, function: Callable, provided_parameters: dict) -> bool:
        """
            Validates the parameters given to the function.
        """
        signature = inspect.signature(function)

        for argument in provided_parameters:
            if argument not in signature.parameters:
                return False

        return True

    def _validate_value(self, function: Callable, value: int) -> bool:

        if value == 0:
            return True

        if value < 0:
            return False

        return hasattr(function, 'payable')

    def entry_point(self, calldata: InternalAgentCalldata, ctx: 'ExecutionContext'):
        """
            The entry point of the InternalAgent, this method is the only method invoked by
            the execution environment. The InternalAgentRequest should be either handled or
            rejected.
        """

        error_response = self.validate_call(calldata, ctx)

        if error_response is not None:
            return error_response, []

        response = getattr(self, calldata.function)(**calldata.parameters)

        return response, ctx.changes
