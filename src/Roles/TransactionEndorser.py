from Role import Role, RoleType


class TransactionEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_ENDORSER)

    def endoreTransaction():
        raise NotImplementedError
