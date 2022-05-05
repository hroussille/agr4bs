import logging
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
        self._behaviors = {}

    @property
    def behaviors(self):
        return self._behaviors

    def bind(self, agent: Agent) -> None:
        logging.debug('Binding %s to %s', self._type, agent.name)
    
    def unbind(self, agent: Agent) -> None:
        logging.debug('Unbinding %s from %s', self._type, agent.name)
