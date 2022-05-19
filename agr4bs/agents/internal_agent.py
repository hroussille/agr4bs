"""
    InternalAgent file class implementation
"""

from .agent import Agent, AgentType


# pylint: disable=too-few-public-methods
class InternalAgentRequest:

    """
        InternalAgentRequest class implementation :

        An InternalAgentRequest is a standard to interact with InternalAgents
        on the Blockchain.
    """

    def __init__(self):
        pass


class InternalAgent(Agent):

    """
        InternalAgent class implementation :

        An InternalAgent is a program in the Blockchain (i.e., Smart Contract).
        It may only act in the system when it is triggered by a transaction coming
        from an ExternalAgent.
    """

    def __init__(self, name: str):
        super().__init__(name, AgentType.INTERNAL_AGENT)

    def entry_point(self, request: InternalAgentRequest):
        """
            The entry point of the InternalAgent, this method is the only method invoked by
            the execution environment. The InternalAgentRequest should be either handled or
            rejected.
        """
