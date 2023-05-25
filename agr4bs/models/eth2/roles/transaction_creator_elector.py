"""
Abstract implementation of the Peer role as per AGR4BS

PeerContextChange:

The PeerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

PeerEndorser:

The Peer implementation which MUST contain the following behaviors :

"""
import random

from ....environment import Environment
from ....agents import AgentType
from ....network.messages import CreateTransaction
from ....roles import Role, RoleType
from ....common import export, every


class TransactionCreatorElector(Role):
    """
        Implementation of the TransactionCreatorElector role
    """

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_CREATOR_ELECTOR, AgentType.EXTERNAL_AGENT)

    @staticmethod
    @export
    @every(minutes=1)
    def elect_transaction_creator(env: Environment):
        """
            Notify a participant that it can create a transaction.
            This is a system event.
        """
        selected = random.choice(env.agents_names)

        env.send_system_message(CreateTransaction(
            env.name, 0, 0, None, "genesis"), selected)
