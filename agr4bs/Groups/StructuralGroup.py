from ..Group import Group, GroupType


class StructuralGroup(Group):

    def __init__(self, name: str) -> None:
        super().__init__(name, GroupType.STRUCTURAL_GROUP)
