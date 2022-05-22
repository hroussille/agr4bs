"""
    InternalAgent file class implementation
"""

from .agent import Agent, AgentType


# pylint: disable=too-few-public-methods
class InternalAgentCall:

    """
        InternalAgentCall class implementation :

        An InternalAgentCall is a standard to interact with InternalAgents
        on the Blockchain.
    """

    def __init__(self, function: str, **parameters):
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


class InternalAgentResponse:

    """
        InternalAgentResponse class implementation :

        An InternalAgentResponse is a standard to receive data back from
        an InternalAgent called through an InternalAgentCall.
    """

    def __init__(self, reverted: bool, revert_reason: str, **return_values):
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


class InternalAgent(Agent):

    """
        InternalAgent class implementation :

        An InternalAgent is a program in the Blockchain (i.e., Smart Contract).
        It may only act in the system when it is triggered by a transaction coming
        from an ExternalAgent.
    """

    def __init__(self, name: str):
        super().__init__(name, AgentType.INTERNAL_AGENT)

    def entry_point(self, request: InternalAgentCall):
        """
            The entry point of the InternalAgent, this method is the only method invoked by
            the execution environment. The InternalAgentRequest should be either handled or
            rejected.
        """

    def fallback(self, request: InternalAgentCall):
        """
            This method is called when receiving no value with data
            It is only called is no other method matches the InternalAgentRequest.
        """
        return InternalAgentResponse(True, "fallback not implemented")

    def receive(self, request: InternalAgentCall) -> InternalAgentResponse:
        """
            This method is called when receiving value without data
        """
        return InternalAgentResponse(True, "cannot receive value")
