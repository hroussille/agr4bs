from ..Agent import StateChange
from ..Role import Role, RoleType


class ContractorStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()


class Contractor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.CONTRACTOR)

    @staticmethod
    def state_change() -> StateChange:
        return ContractorStateChange()
