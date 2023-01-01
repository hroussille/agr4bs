"""
Abstract implementation of the Contractor role as per AGR4BS

ContractorContextChange:

The ContractorContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

Contractor:

The Contractor implementation has no mandatory exports

"""

from ....agents import ContextChange, AgentType
from ....roles import Role, RoleType
from ....common import export


class ContractorContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (Contractor) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        pass


class Contractor(Role):
    """
        Implementation of the Contractor Role which has no mandatory behaviors

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.CONTRACTOR, AgentType.INTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return ContractorContextChange()
