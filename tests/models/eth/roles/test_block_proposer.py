"""
    Test suite for the BlockProposer Role
"""

import agr4bs
from agr4bs.models.eth.blockchain import Block, Transaction

def test_block_proposer_type():
    """
    Ensures that a BlockProposer has the appropriate RoleType
    """
    role = agr4bs.models.eth.roles.BlockProposer()
    assert role.type == agr4bs.RoleType.BLOCK_PROPOSER


def test_block_proposer_behaviors():
    """
    Ensures that a BlockProposer has the appropriate behaviors :

    - select_transaction
    - create_block
    - propose_block

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth.roles.BlockProposer()

    assert 'select_transactions' in role.behaviors
    assert 'create_block' in role.behaviors
    assert 'propose_block' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_block_proposer_addition():
    """
    Ensures that adding a BlockProposer Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCK_PROPOSER Role
    - Agent has all the BlockProposer behaviors
    - Agent has all the BlockProposer context changes
    """
    genesis = Block(None, "genesis")
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth.Factory)
    role = agr4bs.models.eth.roles.BlockProposer()

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth.roles.BlockchainMaintainer())

    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_PROPOSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BLOCK_PROPOSER) == role


def test_block_proposer_removal():
    """
    Ensures that removing a BlockProposer Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCK_PROPOSER Role
    - Agent has none of the BlockProposer behaviors
    - Agent has none of the BlockProposer context changes
    """
    genesis = Block(None, "genesis")
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth.Factory)
    role = agr4bs.models.eth.roles.BlockProposer()

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth.roles.BlockchainMaintainer())

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_PROPOSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context


def test_block_proposer_transaction_selection():
    """
    Ensures that the default transaction selection strategy behaves as expected
    """
    genesis = Block(None, "genesis", [
        Transaction("genesis", "agent_0", 0, 0, 100),
        Transaction("genesis", "agent_1", 0, 0, 100)
    ])

    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth.Factory)

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth.roles.BlockchainMaintainer())
    agent.add_role(agr4bs.models.eth.roles.BlockProposer())
    agent.process_genesis()

    pending_tx1 = Transaction("agent_0", "agent_2", 0, 0, 10)
    pending_tx2 = Transaction("agent_1", "agent_2", 0, 0, 10)
    queued_tx = Transaction("agent_0", "agent_2", 2, 0, 10)

    agent.receive_transaction(pending_tx1)
    agent.receive_transaction(pending_tx2)
    agent.receive_transaction(queued_tx)

    pending_transactions = agent.get_pending_transactions()

    selected_transactions = agent.select_transactions(pending_transactions)

    assert len(selected_transactions) == 2
    assert selected_transactions[0] == pending_tx1
    assert selected_transactions[1] == pending_tx2


def test_block_proposer_block_creation():
    """
    Ensures that the block creation behavior correctly populate a new block
    """
    genesis = Block(None, "genesis", [
                           Transaction("genesis", "agent_0", 0, 0, 100),
                           Transaction("genesis", "agent_1", 0, 0, 100)
                           ])

    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth.Factory)

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.models.eth.roles.BlockchainMaintainer())
    agent.add_role(agr4bs.models.eth.roles.BlockProposer())
    agent.process_genesis()

    pending_tx1 = Transaction("agent_0", "agent_2", 0, 0, 10)
    pending_tx2 = Transaction("agent_1", "agent_2", 0, 0, 10)

    agent.receive_transaction(pending_tx1)
    agent.receive_transaction(pending_tx2)
    agent.can_create_block()

    head = agent.context['blockchain'].head

    # Check proper inclusion in the blockchain
    assert head.hash != genesis.hash
    assert head.parent_hash == genesis.hash

    # Check proper body content according the pending tx
    assert len(head.transactions) == 2
    assert head.transactions[0] == pending_tx1
    assert head.transactions[1] == pending_tx2

    # Check proper state transition according to block content
    assert agent.context['state'].get_account_balance('agent_2') == 20
    assert pending_tx1.hash in agent.context['receipts']
    assert pending_tx2.hash in agent.context['receipts']
