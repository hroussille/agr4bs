from Role import Role, RoleType


class TransactionProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_PROPOSER)

    def createTransaction(self):
        raise NotImplementedError

    def proposeTransaction(self):
        raise NotImplementedError
