from ..Role import Role, RoleType
from ..Agent import Agent, StateChange


class GroupManagerStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        self.groupEnteringPolicy = None


class GroupManager(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.GROUP_MANAGER)

    @staticmethod
    def stateChange() -> StateChange:
        return GroupManagerStateChange()

    @staticmethod
    def authorize(agent: Agent, candidate: Agent, *args, **kwargs) -> bool:
        """ authorizes an agent to enter the group or not

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param candidate: the agent to authorize
            :type agent: Agent
            :returns: wether the agent was authorized or not
            :rtype: bool
        """
        raise NotImplementedError
