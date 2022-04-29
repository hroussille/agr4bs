from Role import Role, RoleType


class Investor(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.INVESTOR)

    def specifyInvestment(self):
        raise NotImplementedError

    def invest(self):
        raise NotImplementedError

    def withdraw(self):
        raise NotImplementedError
