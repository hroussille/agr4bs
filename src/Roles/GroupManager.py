from Role import Role, RoleType


class GroupManager(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.GROUP_MANAGER)

    def authorize():
        raise NotImplementedError
