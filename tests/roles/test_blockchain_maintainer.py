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
