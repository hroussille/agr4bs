from Role import Role, RoleType


class BlockchainMaintainer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER)

    def validateTransaction():
        raise NotImplementedError

    def validateBlock():
        raise NotImplementedError

    def storeTransaction():
        raise NotImplementedError

    def appendBlock():
        raise NotImplementedError

    def executeTransaction():
        raise NotImplementedError
