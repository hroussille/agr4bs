from Role import Role, RoleType


class Agent(object):

    def __init__(self, name: str, initial_balance: int = 0) -> None:
        """ Initializes the Agent interface 

            :param name: the name of the agent
            :type name: str
            :param initial_balance: the initial balance of the agent
            :type initial_balance: int
        """
        self.name = name
        self.balance = initial_balance
        self.roles = {}

    def hasRole(self, role: RoleType) -> bool:
        """ Check whether the agent has a specific Role

            :param role: the role to check for
            :type role: RoleType 
            :returns: wether the agent has the role or not
            :rtype: bool
        """
        return role in self.roles

    def addRole(self, role: Role) -> bool:
        """ Add a specific role to the agent

            :param role: the role to add
            :type role: Role 
            :returns: wether the role was added or not
            :rtype: bool
        """
        if self.hasRole(role.type):
            return False

        self.roles[role.type] = role
        return True

    def removeRole(self, role: Role) -> bool:
        """ Remove a specific role from the agent

            :param role: the role to remove
            :type role: Role 
            :returns: wether the role was removed or not
            :rtype: bool
        """
        if not(self.hasRole(role.type)):
            return False

        self.roles[role.type] = None
        return False

    def getRole(self, role: RoleType) -> Role:
        """ Get a specific Role instance from the Agent

            :param role: the role type to get
            :type role: RoleType
            :returns: the role instance or None
            :rtype: Role
        """
        if not(self.hasRole(role.type)):
            return None

        return self.roles[role]
