from .Agent import Agent
from enum import Enum


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
        self._agent = None

    def bind(self, agent: Agent) -> None:
        if self._agent is not None:
            raise ValueError('Attempting to bind an already binded Role')
        self._agent = agent

    def unbind(self) -> None:
        self._agent = None
