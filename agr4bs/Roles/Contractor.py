"""
Abstract implementation of the Contractor role as per AGR4BS

OracleStateChange:

The OracleStateChange exposes changes that need to be made to the
Agent state when the Role is mounted and unmounted.

Contractor:

The Contractor implementation has no mandatory exports

"""

from ..agent import StateChange
from ..role import Role, RoleType


class ContractorStateChange(StateChange):
    """
        State changes that need to be made to the Agent when
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
        super().__init__(RoleType.CONTRACTOR)

    @staticmethod
    def state_change() -> StateChange:
        return ContractorStateChange()
