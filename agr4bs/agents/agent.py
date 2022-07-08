"""
    Agent file class implementation
"""

from enum import Enum
from .context import Context


class AgentType(Enum):

    """
        Enumeration discerning the allowed types of agents

        - EXTERNAL_AGENT : a blockchain participant
        - INTERNAL_AGENT : a smart contract
    """
    EXTERNAL_AGENT = "external_agent"
    INTERNAL_AGENT = "internal_agent"
    ENVIRONMENT_AGENT = "environment_agent"


class Agent():

    """
        Agent class implementation :

        An Agent is initially an empty shell with no behavior except the native ones.
        It may take on one or several Roles, and expand its behaviors with the ones of
        the Roles it endorsed.
    """

    def __init__(self, name: str, _type: AgentType) -> None:
        """ Initializes the Agent interface

            :param name: the name of the agent
            :type name: str
            :param initial_state: the initial state of the agent
            :type initial_state: dict
        """
        self._name = name
        self._roles = {}
        self._context = Context()
        self._type = _type

    @property
    def name(self) -> str:
        """
            Get the name (i.e., address) of the agent
        """
        return self._name

    @property
    def roles(self) -> 'list[RoleType]':
        """ Get the list of Roles that the Agent is currently playing

            :returns: The list of Roles currently played by the Agent
            :rtype: list[RoleType]
        """
        return list(self._roles.keys())

    @property
    def context(self) -> Context:
        """ Get the current Context of the Agent

            :returns: The current Context of the Agent
            :rtype: Context
        """
        return self._context

    def safe_inject(self, key: str, value: any):
        """
            Safely inject data into the Agent's context.
            raises ValueError if the key already exists.
        """
        if key in self._context:
            raise ValueError(
                "inject_safe won't overwrite existing entry : " + str(key))

        self.unsafe_inject(key, value)

    def unsafe_inject(self, key: str, value: any):
        """
            Injects and possibly overwrites data into the Agent's context
            if the key is already in use.
        """
        self._context[key] = value

    @property
    def type(self) -> AgentType:
        """ Get the type of the Agent

            :returns: The  type of the Agent
            :rtype: RoleType
        """
        return self._type

    def has_role(self, role: 'RoleType') -> bool:
        """ Check whether the agent has a specific Role

            :param role: the role to check for
            :type role: RoleType
            :returns: wether the agent has the role or not
            :rtype: bool
        """
        return role in self._roles

    def has_behavior(self, behavior: str) -> bool:
        """ Check whether the agent has a specific behavior

            :param behavior: the behavior to check for
            :type behavior: str
            :returns: wether the agent has the behavior or not
            :rtype: bool
        """
        return hasattr(self, behavior)

    def add_role(self, role: 'Role') -> bool:
        """ Add a specific role to the agent

            :param role: the role to add
            :type role: Role
            :returns: wether the role was added or not
            :rtype: bool
        """
        if self.has_role(role.type):
            return False

        for dependency in role.dependencies:
            if not self.has_role(dependency):
                error = str(role.type) + " requires : " + str(dependency)
                raise ValueError(error)

        if role.agent_type != self._type:
            raise ValueError(
                "Attempting to add an incompatible Role to an Agent")

        self._roles[role.type] = role
        self._context.apply_context_change(role.context_change())

        for behavior, implementation in role.behaviors.items():
            setattr(self, behavior, implementation.__get__(self, Agent))

        return True

    def remove_role(self, role: 'Role') -> bool:
        """ Remove a specific Role from the Agent

            :param role: the Role to remove
            :type role: Role
            :returns: wether the Role was removed or not
            :rtype: bool
        """
        if not self.has_role(role.type):
            return False

        for behavior in role.behaviors:
            delattr(self, behavior)

        self._context.revert_context_change(role.context_change())

        del self._roles[role.type]

        return True

    def get_role(self, role_type: 'RoleType') -> 'Role':
        """ Get a specific Role instance from the Agent

            :param roleType: the role type to get
            :type roleType: RoleType
            :returns: the role instance or None
            :rtype: Role
        """
        if not self.has_role(role_type):
            return None

        return self._roles[role_type]

    def __getstate__(self):
        state = self.__dict__.copy()

        for role_type, _ in self._roles.items():
            for behavior, _ in self._roles[role_type].behaviors.items():
                if hasattr(self, behavior):
                    del state[behavior]

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        for role_type, _ in self._roles.items():
            for behavior, implementation in self._roles[role_type].behaviors.items():
                setattr(self, behavior, implementation.__get__(self, Agent))
