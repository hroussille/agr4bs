from ..Role import Role, RoleType


class Contractor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.CONTRACTOR)
