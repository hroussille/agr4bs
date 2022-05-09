import logging
from .Agent import Agent, StateChange
from enum import Enum, EnumMeta


class BindBlackListMeta(EnumMeta):
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]


class BindBlackList(Enum, metaclass=BindBlackListMeta):
    STATE_CHANGE = "state_change"


class RoleType(Enum):
    BLOCKCHAIN_MAINTAINER = "BLOCKCHAIN_MAINTAINER"
    BLOCK_PROPOSER = "BLOCK_PROPOSER"
    BLOCK_ENDORSER = "BLOCK_ENDORSER"
    TRANSACTION_PROPOSER = "TRANSACTION_PROPOSER"
    TRANSACTION_ENDORSER = "TRANSACTION_ENDORSER"
    INVESTOR = "INVESTOR"
    INVESTEE = "INVESTEE"
    ORACLE = "ORACLE"
    CONTRACTOR = "CONTRACTOR"
    GROUP_MANAGER = "GROUP_MANAGER"


class Role:

    def __init__(self, type: RoleType) -> None:
        self._type = type

    @staticmethod
    def state_change() -> StateChange:
        return StateChange()

    @property
    def behaviors(self):
        return {behavior: implementation for behavior, implementation in self.__class__.__dict__.items() if behavior not in BindBlackList and isinstance(implementation, staticmethod)}

    @property
    def type(self):
        return self._type
