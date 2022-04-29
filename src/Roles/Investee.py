from Role import Role, RoleType


class Investee(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTEE)

    def redistribute(self):
        raise NotImplementedError
