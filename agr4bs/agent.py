"""
    Agent file class implementation
"""

from copy import deepcopy


class StateChange():

    """
        State changes that need to be made to the Agent when
        the associated Role is either
        mounted or unmounted.
    """

    def mount(self) -> dict:
        """
            Returns the dictionary describing the keys that should be made available
            in the agent state as well as their initial values.
        """
        return self.__dict__

    def unmount(self) -> list:
        """
            Returns the list describing the keys that should be removed from the agent
            state.
        """
        return list(self.__dict__.keys())


class Agent():

    """
        Agent class implementation :

        An Agent is initially an empty shell with no behavior except the native ones.
        It may take on one or several Roles, and expand its behaviors with the ones of
        the Roles it endorsed.
    """

    def __init__(self, name: str, initial_state: dict = None) -> None:
        """ Initializes the Agent interface

            :param name: the name of the agent
            :type name: str
            :param initial_state: the initial state of the agent
            :type initial_state: dict
        """
        self.name = name
        self._roles = {}

        if initial_state is None:
            initial_state = {}

        self._state = {} | deepcopy(initial_state)

    @property
    def roles(self) -> 'list[RoleType]':
        """ Get the list of Roles that the Agent is currently playing

            :returns: The list of Roles currently played by the Agent
            :rtype: list[RoleType]
        """
        return list(self._roles.keys())

    @property
    def state(self) -> dict:
        """ Get the current state view of the Agent

            :returns: The current state view of the Agent
            :rtype: dict
        """
        return self._state

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

        self._roles[role.type] = role
        self._state |= role.state_change().mount()

        for behavior, implementation in role.behaviors.items():
            setattr(self, behavior, implementation)

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

        for state_property in role.state_change().unmount():
            del self._state[state_property]

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
