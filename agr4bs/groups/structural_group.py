"""
    StructuralGroup file class implementation
"""

from .group import Group, GroupType


class StructuralGroup(Group):

    """
        StructuralGrouo class implementation :

        A StructuralGroup is a subtype of Group (collection of Agents)
        that work together to provide a functionality or service.

        This functionality or service is ESSENTIAL to the system.

        ex:
            - Transaction Management Group
            - Block Management Group
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, GroupType.STRUCTURAL_GROUP)
