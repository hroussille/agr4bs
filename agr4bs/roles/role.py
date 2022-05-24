
"""
    Role file class implementation
"""

from enum import Enum
from ..common import IterableEnumMeta
from ..agents import ContextChange, AgentType


class BindBlackList(Enum, metaclass=IterableEnumMeta):
    """
        Enumeration of the black listed Roles static methods
        (i.e., behaviors).

        All names present in this enum should not be exported by
        any Role nor they should be imported by any Agent.
    """
    CONTEXT_CHANGE = "context_change"


class RoleType(Enum):

    """
        Enumeration of all known Role types

        Every Role should identify itself with a value contained
        in this enumeration.
    """

    BLOCKCHAIN_MAINTAINER = "BLOCKCHAIN_MAINTAINER"
    BLOCK_PROPOSER = "BLOCK_PROPOSER"
    BLOCK_BUILDER = "BLOCK_SEQUENCER"
    BLOCK_ENDORSER = "BLOCK_ENDORSER"
    BLOCK_SEQUENCER = "BLOCK_SEQUENCER"
    TRANSACTION_PROPOSER = "TRANSACTION_PROPOSER"
    TRANSACTION_ENDORSER = "TRANSACTION_ENDORSER"
    INVESTOR = "INVESTOR"
    INVESTEE = "INVESTEE"
    ORACLE = "ORACLE"
    CONTRACTOR = "CONTRACTOR"
    GROUP_MANAGER = "GROUP_MANAGER"
    PEER = "PEER"


class Role:

    """
        Role class implementation :

        A Role is collection of behaviors to accomplish a specific
        set of functionalities on the Blockchain.
    """

    def __init__(self, _type: RoleType, agent_type: AgentType, dependencies: list[RoleType] = None) -> None:
        self._type = _type
        self._agent_type = agent_type
        self._event_handlers = {}

        if dependencies is None:
            dependencies = []

        self._dependencies = dependencies

    @staticmethod
    def context_change() -> ContextChange:
        """
            The context_change static method should return a ContextChange object
            describing the changes needed to the context whenever the Role is
            mounted or unmounted from an Agent.

            Each concrete Role implementation MUST redefine this method as well
            as define its own RoleNameContextChange class to be independant of every
            other Roles.
        """
        return ContextChange()

    @property
    def dependencies(self) -> list[RoleType]:
        """
            The dependencies function should return the list of RoleTypes that this Role relies on.
        """
        return self._dependencies

    @property
    def event_handlers(self) -> dict:
        """ Get the event handlers of the Role

            :returns: the dictionary of
        """
    @property
    def behaviors(self) -> dict:
        """ Get the behaviors exposed by the Role

            :returns: the dictionary of behaviors with the format {behavior_name: behavior_implementation}
            :rtype: dict
        """
        return {behavior: getattr(self, behavior) for behavior, implementation in self.__class__.__dict__.items() if behavior not in BindBlackList and isinstance(implementation, staticmethod)}

    @property
    def type(self) -> RoleType:
        """ Get the type of the Role as per the RoleType Enumeration

            :returns: the RoleType of the Role
            :rtype: RoleType
        """
        return self._type

    @property
    def agent_type(self) -> AgentType:
        """ Get the AgentType the Role is able to be mounted to

            :returns: the AgentType the Role can be mounted to
            :rtype: AgentType
        """
        return self._agent_type
