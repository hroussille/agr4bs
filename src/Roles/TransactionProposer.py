from Role import Role, RoleType
from Agent import Agent
from Common.Transaction import Transaction, Payload


class TransactionProposer(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_PROPOSER)

    def createTransaction(self, paylaod: Payload, receiver: Agent):
        """ Create a transaction with the given payload for the given receiver

            :param paylaod: the payload of the transaction
            :type payload: Payload
            :param receiver: the receiver of the transaction
            :type receiver: Agent
        """
        raise NotImplementedError

    def proposeTransaction(self, transaction: Transaction, *args, **kwargs):
        """ Propose a transaction to the network

            :param block: the transaction to propose to the network
            :type block: Transaction
        """
        raise NotImplementedError
