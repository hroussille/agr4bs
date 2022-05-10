"""
Abstract implementation of the Oracle role as per AGR4BS

OracleStateChange:

The OracleStateChange exposes changes that need to be made to the
Agent state when the Role is mounted and unmounted.

Oracle:

The Oracle implementation has no mandatory exports

"""

from agr4bs.agent import StateChange
from ..role import Role, RoleType


class OracleStateChange(StateChange):
    """
        State changes that need to be made to the Agent when
        the associated Role (Oracle) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        pass


class Oracle(Role):
    """
        Implementation of the Oracle Role which has no mandatory behaviors

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.ORACLE)

    @staticmethod
    def state_change() -> StateChange:
        return OracleStateChange()
