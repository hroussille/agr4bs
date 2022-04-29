from Role import Role, RoleType


class BlockchainMaintainer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER)

    def validateTransaction(self):
        raise NotImplementedError

    def validateBlock(self):
        raise NotImplementedError

    def storeTransaction(self):
        raise NotImplementedError

    def appendBlock(self):
        raise NotImplementedError

    def executeTransaction(self):
        raise NotImplementedError
