"""
    Test suite for the BlockchainMaintainer Role
"""

import agr4bs


def test_blockchain_maintainer_type():
    """
    Ensures that a BlockchainMaintainer has the appropriate RoleType
    """
    role = agr4bs.roles.BlockchainMaintainer()
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
    role = agr4bs.roles.BlockchainMaintainer()

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
    genesis = agr4bs.Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.Factory)
    role = agr4bs.roles.BlockchainMaintainer()

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
    genesis = agr4bs.Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.Factory)
    role = agr4bs.roles.BlockchainMaintainer()

    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(role)

    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCKCHAIN_MAINTAINER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context


def test_blockchain_maintainer_valid_reorg():
    """
    Ensures that blockchain maintainer handles reorgs on valid blocks correctly
    """
    genesis = agr4bs.Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.Factory)
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.roles.BlockchainMaintainer())

    #
    #          / block_1 -> block_2
    #  genesis
    #          \ block_3 -> block_4 -> block_5
    #

    block_1 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_2 = agr4bs.Block(block_1.hash, "agent_0", [])

    block_3 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_4 = agr4bs.Block(block_3.hash, "agent_0", [])
    block_5 = agr4bs.Block(block_4.hash, "agent_0", [])

    agent.receive_block(block_1)
    agent.receive_block(block_2)

    assert agent.context["blockchain"].head == block_2

    agent.receive_block(block_3)
    agent.receive_block(block_4)
    agent.receive_block(block_5)

    assert agent.context["blockchain"].head == block_5

    assert not agent.context["blockchain"].is_block_on_main_chain(block_2)

def test_blockchain_maintainer_invalid_reorg():
    """
    Ensures that blockchain maintainer handles reorgs on valid blocks correctly
    """
    genesis = agr4bs.Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.Factory)
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.roles.BlockchainMaintainer())

    #
    #          / block_1 -> block_2
    #  genesis
    #          \ block_3 -> block_4 -> block_5 -> block_6 (INVALID)
    #

    invalid_tx = agr4bs.Transaction("invalid", "invalid", 0, 0, 1);

    block_1 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_2 = agr4bs.Block(block_1.hash, "agent_0", [])

    block_3 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_4 = agr4bs.Block(block_3.hash, "agent_0", [])
    block_5 = agr4bs.Block(block_4.hash, "agent_0", [])
    block_6 = agr4bs.Block(block_5.hash, "agent_0", [invalid_tx])

    agent.receive_block(block_1)
    agent.receive_block(block_2)

    assert agent.context["blockchain"].head == block_2

    agent.receive_block(block_3)
    agent.receive_block(block_4)
    agent.receive_block(block_5)
    agent.receive_block(block_6)

    assert agent.context["blockchain"].head == block_5

    assert not agent.context["blockchain"].is_block_on_main_chain(block_2)
    assert not agent.context["blockchain"].is_block_on_main_chain(block_6)
    assert agent.context["blockchain"].get_block(block_6.hash).invalid
    assert agent.context["state"].get_account_balance("agent_0") == 30


def test_blockchain_maintainer_delayed_invalid_reorg():

    """
    Ensures that blockchain maintainer handles reorgs on valid blocks correctly
    """
    
    genesis = agr4bs.Block(None, None, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.Factory)
    agent.add_role(agr4bs.roles.Peer())
    agent.add_role(agr4bs.roles.BlockchainMaintainer())

    #
    #          / block_1 -> block_2
    #  genesis
    #          \ block_3 -> block_4 -> block_5 -> block_6 (INVALID) -> block_7
    #

    invalid_tx = agr4bs.Transaction("invalid", "invalid", 0, 0, 1);
    valid_tx = agr4bs.Transaction("agent_0", "agent_1", 0, 0, 10)

    block_1 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_2 = agr4bs.Block(block_1.hash, "agent_0", [])

    block_3 = agr4bs.Block(genesis.hash, "agent_0", [])
    block_4 = agr4bs.Block(block_3.hash, "agent_0", [])
    block_5 = agr4bs.Block(block_4.hash, "agent_0", [])
    block_6 = agr4bs.Block(block_5.hash, "agent_0", [valid_tx, invalid_tx])
    block_7 = agr4bs.Block(block_6.hash, "agent_0", [])

    agent.receive_block(block_1)
    agent.receive_block(block_2)

    assert agent.context["blockchain"].head == block_2

    agent.receive_block(block_3)
    agent.receive_block(block_4)
    agent.receive_block(block_5)
    agent.receive_block(block_7)
    agent.receive_block(block_6)

    assert agent.context["blockchain"].head == block_5

    assert not agent.context["blockchain"].is_block_on_main_chain(block_2)
    assert not agent.context["blockchain"].is_block_on_main_chain(block_6)
    assert agent.context["blockchain"].get_block(block_6.hash).invalid
