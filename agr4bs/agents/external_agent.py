"""
    ExternalAgent file class implementation
"""

from .agent import Agent, AgentType
from ..common import Block


class ExternalAgent(Agent):

    """
        ExternalAgent class implementation :

        An ExternalAgent is a participant in the Blockchain (i.e., EOA).
        It may contribute to the system or simply interact with it autonomously.
    """

    def __init__(self, name: str, genesis: Block):

        super().__init__(name, AgentType.EXTERNAL_AGENT)

        self._context['genesis'] = genesis
