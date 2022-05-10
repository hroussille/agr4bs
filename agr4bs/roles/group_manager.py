"""
Abstract implementation of the GroupManager role as per AGR4BS

GroupManagerStateChange:

The GroupManagerStateChange exposes changes that need to be made to the
Agent state when the Role is mounted and unmounted.

GroupManager:

The GroupManager implementation which MUST contain the following behaviors :
- authorize
"""

from ..role import Role, RoleType
from ..agent import Agent, StateChange


class GroupManagerStateChange(StateChange):
    """
        State changes that need to be made to the Agent when
        the associated Role (GroupManager) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.group_entering_policy = None


class GroupManager(Role):

    """
        Implementation of the GroupManager Role which must
        expose the following behaviors :
        - authorize

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.GROUP_MANAGER)

    @staticmethod
    def state_change() -> StateChange:
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
