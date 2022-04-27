from Agent import Agent
from enum import Enum


class GroupType:
    INTEREST_GROUP = "INTEREST_GROUP"
    STRUCTURAL_GROUP = "STRUCTURAL_GROUP"


class Group:

    def __init__(self, name: str, type: GroupType) -> None:
        """ Initializes the Group interface 

            :param name: the name of the group
            :type name: str
            :param type: the type of the group
            :type type: GroupType
        """
        self.name = name
        self.type = type
        self.members = {}

    def hasMember(self, agent: Agent) -> bool:
        """ Check whether a specific agent is part of the group

            :param agent: the agent to check membership for
            :type agent: Agent
            :returns: wether the agent is in the group or not
            :rtype: bool
        """
        return agent in self.members

    def addMember(self, agent: Agent) -> bool:
        """ Add a specific agent to the group

            :param agent: the agent to add to the group
            :type agent: Agent
            :returns: wether the agent was added to the group or not
            :rtype: bool
        """
        if not(self.hasMember(agent)):
            self.members[agent] = agent
            return True
        return False

    def removeMember(self, agent: Agent) -> bool:
        """ Remove a specific agent from the group

            :param agent: the agent to remove from the group
            :type agent: Agent
            :returns: wether the agent was removed from the group or not
            :rtype bool 
        """
        if self.has(agent):
            self.members[agent] = None
            return True
        return False
