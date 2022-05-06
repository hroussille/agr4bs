from copy import deepcopy


class StateChange(object):

    def __init__(self) -> None:
        pass

    def mount(self) -> dict:
        return self.__dict__

    def unmount(self) -> list:
        return list(self.__dict__.keys())


class Agent(object):

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
    def roles(self):
        return self._roles

    @property
    def state(self):
        return self._state

    def hasRole(self, role: 'RoleType') -> bool:
        """ Check whether the agent has a specific Role

            :param role: the role to check for
            :type role: RoleType
            :returns: wether the agent has the role or not
            :rtype: bool
        """
        return role in self._roles

    def hasBehavior(self, behavior: str) -> bool:
        return hasattr(self, behavior)

    def addRole(self, role: 'Role') -> bool:
        """ Add a specific role to the agent

            :param role: the role to add
            :type role: Role
            :returns: wether the role was added or not
            :rtype: bool
        """
        if self.hasRole(role.type):
            return False

        self._roles[role.type] = role
        self._state |= role.stateChange().mount()

        for behavior, implementation in role.behaviors.items():
            setattr(self, behavior, implementation)

        return True

    def removeRole(self, role: 'Role') -> bool:
        """ Remove a specific role from the agent

            :param role: the role to remove
            :type role: Role
            :returns: wether the role was removed or not
            :rtype: bool
        """
        if not(self.hasRole(role.type)):
            return False

        for behavior in role.behaviors:
            delattr(self, behavior)

        for stateProperty in role.stateChange().unmount():
            del self._state[stateProperty]

        del self._roles[role.type]

        return True

    def getRole(self, roleType: 'RoleType') -> 'Role':
        """ Get a specific Role instance from the Agent

            :param roleType: the role type to get
            :type roleType: RoleType
            :returns: the role instance or None
            :rtype: Role
        """
        if not(self.hasRole(roleType)):
            return None

        return self._roles[roleType]
