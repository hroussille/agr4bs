from agr4bs.Agent import StateChange
from ..Role import Role, RoleType


class OracleStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()


class Oracle(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.ORACLE)

    @staticmethod
    def state_change() -> StateChange:
        return OracleStateChange()
