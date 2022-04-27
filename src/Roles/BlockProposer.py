from Role import Role, RoleType


class BlockProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_PROPOSER)

    def selectTransaction():
        raise NotImplementedError

    def createBlock():
        raise NotImplementedError

    def proposeBlock():
        raise NotImplementedError
