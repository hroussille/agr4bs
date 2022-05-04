from ..Role import Role, RoleType


class Oracle(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.ORACLE)
