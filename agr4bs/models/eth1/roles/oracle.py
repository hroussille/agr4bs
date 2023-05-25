"""
Abstract implementation of the Oracle role as per AGR4BS

OracleContextChange:

The OracleContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

Oracle:

The Oracle implementation has no mandatory exports

"""

from ....agents import ContextChange, AgentType
from ....roles import Role, RoleType


class OracleContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
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
        super().__init__(RoleType.ORACLE, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required when mounting / unmounting the Role
        """
        return OracleContextChange()
