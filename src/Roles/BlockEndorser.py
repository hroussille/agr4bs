from Role import Role, RoleType


class BlockEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_ENDORSER)

    def endorseBlock():
        raise NotImplementedError
