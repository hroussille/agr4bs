"""
    InterestGroup file class implementation
"""

from ..group import Group, GroupType


class InterestGroup(Group):

    """
        InterestGrouo class implementation :

        An InterestGroup is a subtype of Group (collection of Agents)
        that work together to provide a functionality or service.

        This functionality or service is NON ESSENTIAL to the system.

        ex:
            - Mining pools
            - Staking pools
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, GroupType.INTEREST_GROUP)
