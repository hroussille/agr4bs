from Role import Role, RoleType
from Agent import Agent


class GroupManager(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.GROUP_MANAGER)

    def authorize(self, agent: Agent, *args, **kwargs) -> bool:
        """ authorizes an agent to enter the group or not

            :param agent: the agent to authorize
            :type agent: Agent
            :returns: wether the agent was authorized or not
            :rtype: bool
        """
        raise NotImplementedError
