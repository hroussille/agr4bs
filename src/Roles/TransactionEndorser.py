from Role import Role, RoleType
from Common.Transaction import Transaction


class TransactionEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.TRANSACTION_ENDORSER)

    def endoreTransaction(self, transaction: Transaction) -> bool:
        """ Endorse a specific transaction

            :param transaction: the transaction to endorse
            :type transaction: Transaction
            :returns: wether the transaction was endorsed or not
            :rtype: bool
        """
        raise NotImplementedError
