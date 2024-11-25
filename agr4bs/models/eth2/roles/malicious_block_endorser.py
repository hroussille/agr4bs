
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


class MaliciousBlockEndorserContextChange(ContextChange):

    """
        Context changes that need to be made to the Agent when
        the associated Role (BlockEndorser) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        super().__init__()

        self.attestation_done = False
        self.malicious = True
        self.malicious_attester= True
        self.next_proposer_is_malicious = False
        self.current_proposer_is_malicious = False


class MaliciousBlockEndorser(Role):

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
        return MaliciousBlockEndorserContextChange()

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
        current_proposer_is_malicious = agent.context['current_proposer_is_malicious']
        next_proposer_is_malicious = agent.context['next_proposer_is_malicious']
        head = None
        action = None

        # Case 1 : Attest honestly
        # This is done only if the next or current proposer is not malicious
        if not next_proposer_is_malicious and not current_proposer_is_malicious:
            action = "HONEST ATTESTATION"
            head = blockchain.get_block(agent.get_head())
            print("Attesting honestly" + head.hash)
            
        # Case 2 : Attest to the parent of the head block
        # This is done if the next proposer is malicious to give the head an advantage through proposer boost
        if next_proposer_is_malicious:
            action = "MALICIOUS ATTESTATION (N - 1)"
            head = blockchain.get_block(blockchain.get_block(agent.get_head()).parent_hash)
            print("Attesting to the parent of the head block" + head.hash)

        # Case 3 : Attest for the current malicious block
        # This is done if the current proposer is malicious to give more weight to the malicious block
        if current_proposer_is_malicious:
            action = "MALICIOUS ATTESTATION (N)"
            candidates = blockchain.get_blocks_for_slot(agent.context['slot'])
            assert len(candidates) == 1
            head = candidates[0]
            print("Attesting for the current malicious block : " + head.hash)

        agent.context["factory"].push_attester_history([current_proposer_is_malicious, next_proposer_is_malicious, agent.context["slot"]], action)

        # Process any necessary reorg before endorsing the block
        if head.hash != blockchain.head.hash:
            reverted_blocks, added_blocks = blockchain.find_path(blockchain.head, head)
            agent.reorg(reverted_blocks, added_blocks)

        assert head.hash == blockchain.head.hash
        
        # This is the block that we are endorsing as the head of the chain
        root = blockchain.head

        # This is the checkpoint that we are attesting to :
        # - source is the last justified checkpoint extending the finalized chain
        # - target is the last non-justified checkpoint extending the source
        
        source = agent.context['beacon_states'][root.hash].current_justified_checkpoint()
        target = blockchain.get_checkpoint_from_epoch(agent.context['epoch'], root)

        attestation = Attestation(agent.name, agent.context['epoch'], agent.context['slot'], agent.context['index'], root.hash, source.hash, target.hash)
        validators = agent.context['beacon_states'][root.hash].validators
        
        agent.send_system_message(DiffuseBlockEndorsement(agent.name, attestation), validators)
 