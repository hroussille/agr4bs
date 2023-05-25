"""
Abstract implementation of the BlockEndorser role as per AGR4BS

BlockEndorserContextChange:

The BlockEndorserContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

BlockEndorser:

The BlockEndorser implementation which MUST contain the following behaviors :
- endorse_block
"""

from ....agents import Agent, ContextChange, AgentType
from ....roles import Role, RoleType
from ..blockchain import Block
from ....common import export


class BlockEndorserContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (BlockEndorser) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        super().__init__()

        def _block_endorsement_strategy():
            return True

        self.block_endorsement_strategy = _block_endorsement_strategy


class BlockEndorser(Role):
    """
        Implementation of the BlockEndorser Role which must
        expose the following behaviors :
        - endorse_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.BLOCK_ENDORSER, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockEndorserContextChange()

    @staticmethod
    @export
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
