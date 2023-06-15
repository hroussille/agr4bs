"""
    Test suite for the BlockchainMaintainer Role
"""

import agr4bs

from agr4bs.models.eth2.blockchain import Block, Transaction

def test_blockchain_maintainer_type():
    """
    Ensures that a BlockchainMaintainer has the appropriate RoleType
    """
    role = agr4bs.models.eth2.roles.BlockchainMaintainer()
    assert role.type == agr4bs.RoleType.BLOCKCHAIN_MAINTAINER

def test_blockchain_maintainer_behaviors():
    """
    Ensures that a BlockchainMaintainer has the appropriate behaviors :

    - append_block
    - execute_transaction
    - validate_block
    - validate_transaction
    - store_transaction

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth2.roles.BlockchainMaintainer()

    assert 'append_block' in role.behaviors
    assert 'execute_transaction' in role.behaviors
    assert 'validate_block' in role.behaviors
    assert 'validate_transaction' in role.behaviors
    assert 'store_transaction' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_blockchain_maintainer_addition():
    """
    Ensures that adding a BlockchainMaintainer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCKCHAIN_MAINTAINER Role
    - Agent has all the BlockchainMaintainer behaviors
    - Agent has all the BlockchainMaintainer context changes
    """
    genesis = Block(None, None, 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    role = agr4bs.models.eth2.roles.BlockchainMaintainer()

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(role)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BLOCKCHAIN_MAINTAINER) == role


def test_blockchain_maintainer_removal():
    """
    Ensures that removing a BlockchainMaintainer Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCKCHAIN_MAINTAINER Role
    - Agent has none of the BlockchainMaintainer behaviors
    - Agent has none of the BlockchainMaintainer context changes
    """
    genesis = Block(None, None, 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    role = agr4bs.models.eth2.roles.BlockchainMaintainer()

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(role)

    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCKCHAIN_MAINTAINER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context


def test_blockchain_maintainer_receive_attestation():
    """
        Ensures that blockchain maintainer handles attestations correctly
        - Block votes should be taken into account immediately as latest messages
        - Checkpoint votes should be staged until they are included in a block

        We must stage the checkpoint votes because we may be the agent that
        creates the block that includes the checkpoint vote.
    """
    genesis = Block(None, None, 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())

    agent.next_epoch(0, ["agent_0"])

    root = genesis.hash
    source = genesis.hash
    target = genesis.hash

    attestation = agr4bs.models.eth2.blockchain.Attestation(agent.name, 0, 0, 0, root, source, target)
    
    agent.receive_attestation(attestation)

    assert agent.context["latest_messages"][agent.name] == attestation
    assert agent.context["attestations"] == []
    assert attestation in agent.context['pending_attestations']


def test_blockchain_maintainer_merge_pending_attestations():
    """
        Ensures that blockchain maintainer handles next slot correctly
        The pending attestations should be added to the attestations
    """
    genesis = Block(None, None, 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())

    agent.next_epoch(0, ["agent_0", "agent_1"])

    root = genesis.hash
    source = genesis.hash
    target = genesis.hash

    attestation1 = agr4bs.models.eth2.blockchain.Attestation("agent_0", 0, 0, 0, root, source, target)
    attestation2 = agr4bs.models.eth2.blockchain.Attestation("agent_1", 0, 0, 0, root, source, target)

    agent.context['slot'] = 0
    agent.context['attestations'] = [attestation1]

    agent.receive_attestation(attestation2)

    assert agent.context["latest_messages"]["agent_1"] == attestation2
    assert agent.context["attestations"] == [attestation1]
    assert attestation2 in agent.context['pending_attestations']

    agent.merge_pending_attestations(1, [f"agent_{i}" for i in range(32)])

    assert agent.context["attestations"] == [attestation1, attestation2]
    assert agent.context["pending_attestations"] == []


def test_blockchain_maintainer_tx_pool():
    """
        Ensures that the tx_pool is correctly updated and that the query for pending transactions
        yields the expected result
    """
    genesis = Block(
        None, "genesis", 0, [Transaction("genesis", "agent_0", 0, 0, 100)])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())
    agent.process_genesis()

    pending_tx = Transaction("agent_0", "agent_1", 0, 0, 10)
    queued_tx = Transaction("agent_0", "agent_1", 2, 0, 10)

    agent.receive_transaction(pending_tx)

    assert len(agent.context['tx_pool']) == 1
    assert len(agent.context['tx_pool']['agent_0']) == 1

    pending_transactions = agent.get_pending_transactions()

    assert len(pending_transactions) == 1
    assert len(pending_transactions['agent_0']) == 1
    assert pending_transactions['agent_0'][0] == pending_tx

    agent.receive_transaction(queued_tx)

    assert len(agent.context['tx_pool']) == 1
    assert len(agent.context['tx_pool']['agent_0']) == 2

    pending_transactions = agent.get_pending_transactions()

    assert len(pending_transactions) == 1
    assert len(pending_transactions['agent_0']) == 1
    assert pending_transactions['agent_0'][0] == pending_tx

    fill_tx = Transaction("agent_0", "agent_1", 1, 0, 10)

    agent.receive_transaction(fill_tx)

    assert len(agent.context['tx_pool']) == 1
    assert len(agent.context['tx_pool']['agent_0']) == 3

    pending_transactions = agent.get_pending_transactions()

    assert len(pending_transactions) == 1
    assert len(pending_transactions['agent_0']) == 3
    assert pending_transactions['agent_0'][0] == pending_tx
    assert pending_transactions['agent_0'][1] == fill_tx
    assert pending_transactions['agent_0'][2] == queued_tx


def test_blockchain_maintainer_replace_transaction():
    """
       Ensures that a tx can only be replaced if some predefined conditions are met:
       a tx can only be replaced if another tx with the same nonce and higher fee is
       provided before the tx to replace is included in a block.
    """
    genesis = Block(None, "genesis", 0, [Transaction(
        "genesis", "agent_0", nonce=0, value=10)])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())
    agent.process_genesis()

    tx = Transaction("agent_0", "agent_1", nonce=0, fee=0)
    replacement_tx = Transaction("agent_0", "agent_1", nonce=0, fee=0)

    assert agent.receive_transaction(tx)
    assert agent.receive_transaction(replacement_tx) is False
    assert agent.context['tx_pool']['agent_0'][0] == tx

    replacement_tx = Transaction("agent_0", "agent_1", nonce=0, fee=1)

    assert agent.receive_transaction(replacement_tx)
    assert agent.context['tx_pool']['agent_0'][0] == replacement_tx
