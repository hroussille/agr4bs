from Role import Role, RoleType


class BlockProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_PROPOSER)

    def selectTransaction(self):
        raise NotImplementedError

    def createBlock(self):
        raise NotImplementedError

    def proposeBlock(self):
        raise NotImplementedError
