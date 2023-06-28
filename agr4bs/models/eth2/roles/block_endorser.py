
"""
Ethereum 2.0 implementation of the BlockEndorser role as per AGR4BS

BlockEndorserContextChange:

The BlockEndorserContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

BlockEndorser:

The BlockEndorser implementation which MUST contain the following behaviors :
- endorse_block
"""

import datetime
from ....agents import ExternalAgent, ContextChange, AgentType
from ....roles import Role, RoleType
from ..blockchain import Attestation
from ....common import export, on
from ....network.messages import RequestBlockEndorsement, DiffuseBlockEndorsement
from ....events import REQUEST_BLOCK_ENDORSEMENT, NEXT_SLOT


class BlockEndorserContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (BlockEndorser) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        super().__init__()

        self.attestation_done = False


class BlockEndorser(Role):

    """
        In Ethereum 2.0 the block endorser role votes for block in the beacon chain
    """

    def __init__(self) -> None:
        dependencies = [RoleType.BLOCKCHAIN_MAINTAINER]
        super().__init__(RoleType.BLOCK_ENDORSER, AgentType.EXTERNAL_AGENT, dependencies)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockEndorserContextChange()

    @staticmethod
    @on(NEXT_SLOT)
    @export
    def reset_attestation_flag(agent: ExternalAgent, slot:int, attesters: list[str]):
        """
            Reset the attestation flag
        """
        agent.context['attestation_done'] = False

        # Schedule the endorsement of the block if the agent is an attester
        # and no block was received before 1/3 of the slot time has elapsed
        if agent.name in attesters:
            agent.schedule_behavior('endorse_block', datetime.timedelta(seconds=4))

    @staticmethod
    @on(REQUEST_BLOCK_ENDORSEMENT)
    @export
    def endorse_block(agent: ExternalAgent):
        """
            Send the Ethereum 2.0 attestation when requested
            This can happen in two cases:

            1- A new block has been received
            2- 1/3 of the slot time has elapsed
        """

        if agent.context['attestation_done']:
            return
        
        blockchain = agent.context['blockchain']

        # Process the block votes that we received in slot n - 1
        # This will (hopefully) consensually update the blockchain head
        # A reorg may be triggered if the local view of the blockchain is not the same as the network's
        reverted_blocks, appended_blocks = blockchain.process_block_votes(agent.context['attestations'])
        agent.reorg(reverted_blocks, appended_blocks)

        # This is the block that we are endorsing as the head of the chain
        root = blockchain.head

        # This is the checkpoint that we are attesting to :
        # - source is the last justified checkpoint extending the finalized chain
        # - target is the last non-justified checkpoint extending the source
        
        source = agent.context['beacon_states'][root.hash].current_justified_checkpoint()
        target = blockchain.get_checkpoint_from_epoch(agent.context['epoch'], root)

        attestation = Attestation(agent.name, agent.context['epoch'], agent.context['slot'], agent.context['index'], root.hash, source.hash, target.hash)
        validators = agent.context['beacon_states'][root.hash].validators
        
        agent.send_message(DiffuseBlockEndorsement(agent.name, attestation), validators)
 