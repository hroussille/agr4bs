from ..Agent import Agent, StateChange
from ..Role import Role, RoleType
from ..Common import Block


class BlockEndorserStateChange(StateChange):

    def __init__(self) -> None:
        super().__init__()

        def _block_endorsement_strategy():
            return True

        self.block_endorsement_strategy = _block_endorsement_strategy


class BlockEndorser(Role):

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_ENDORSER)

    @staticmethod
    def state_change() -> StateChange:
        return BlockEndorserStateChange()

    @staticmethod
    def endorse_block(agent: Agent, block: Block, *args, **kwargs) -> bool:
        """ Endorse a specific block

            :param agent: the agent on which the behavior operates
            :type agent: Agent
            :param block: the block to endorse
            :type block: Block
            :returns: wether the block was endorsed or not
            :rtype: bool
        """
        raise NotImplementedError
