from Group import Group, GroupType


class InterestGroup(Group):

    def __init__(self, name: str) -> None:
        super().__init__(name, GroupType.INTEREST_GROUP)
