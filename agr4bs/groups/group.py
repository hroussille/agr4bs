
"""
    Group file class implementation
"""

from enum import Enum
from ..agents import Agent


class GroupType(Enum):

    """
        Enumeration of all known Group types

        Every Group should identify itself with a value contained
        in this enumeration.
    """

    INTEREST_GROUP = "INTEREST_GROUP"
    STRUCTURAL_GROUP = "STRUCTURAL_GROUP"


class Group:

    """
        Group class implementation :

        A Group is a collection of Agents working together towards
        a common goal.
    """

    def __init__(self, name: str, _type: GroupType) -> None:
        """ Initializes the Group interface

            :param name: the name of the group
            :type name: str
            :param type: the type of the group
            :type type: GroupType
        """
        self.name = name
        self.type = _type
        self.members = {}

    def has_member(self, agent: Agent) -> bool:
        """ Check whether a specific agent is part of the group

            :param agent: the agent to check membership for
            :type agent: Agent
            :returns: wether the agent is in the group or not
            :rtype: bool
        """
        return agent in self.members

    def add_member(self, agent: Agent) -> bool:
        """ Add a specific agent to the group

            :param agent: the agent to add to the group
            :type agent: Agent
            :returns: wether the agent was added to the group or not
            :rtype: bool
        """
        if not self.has_member(agent):
            self.members[agent] = agent
            return True

        return False

    def remove_member(self, agent: Agent) -> bool:
        """ Remove a specific agent from the group

            :param agent: the agent to remove from the group
            :type agent: Agent
            :returns: wether the agent was removed from the group or not
            :rtype bool
        """
        if self.has_member(agent):
            self.members[agent] = None
            return True
        return False
