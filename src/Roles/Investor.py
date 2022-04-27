from Role import Role, RoleType


class Investor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTOR)

    def specifyInvestment():
        raise NotImplementedError

    def invest():
        raise NotImplementedError

    def withdraw():
        raise NotImplementedError
