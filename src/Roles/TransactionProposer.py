from Role import Role, RoleType


class TransactionProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_PROPOSER)

    def createTransaction():
        raise NotImplementedError

    def proposeTransaction():
        raise NotImplementedError
