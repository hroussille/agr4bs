from Role import Role, RoleType
from Common import Block


class BlockEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_ENDORSER)
        self._endorsementStrategy = None

    @property
    def endorsementStrategy(self):
        return self._endorsementStrategy

    @endorsementStrategy.setter
    def endorsementStrategy(self, newEndorsementStrategy):
        self._endorsementStrategy = newEndorsementStrategy

    @endorsementStrategy.deleter
    def endorsementStrategy(self):
        del self._endorsementStrategy

    def endorseBlock(self, block: Block) -> bool:
        """ Endorse a specific block

            :param block: the block to endorse
            :type block: Block
            :returns: wether the block was endorsed or not
            :rtype: bool
        """
        raise NotImplementedError
