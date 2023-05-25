"""
    Test suite for the BlockEndorser Role
"""

import datetime
import agr4bs


def test_block_endorser_type():
    """
    Ensures that a BlockEndorser has the appropriate RoleType
    """
    role = agr4bs.models.eth2.roles.BlockEndorser()
    assert role.type == agr4bs.RoleType.BLOCK_ENDORSER


def test_block_endorser_behaviors():
    """
    Ensures that a BlockEndorser has the appropriate behaviors :

    - endorse_block

    Also ensures that the `context_change` static method is NOT exported.
    """
    role = agr4bs.models.eth2.roles.BlockEndorser()

    assert 'endorse_block' in role.behaviors
    assert 'reset_attestation_flag' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_block_endorser_addition():
    """
    Ensures that adding a BlockEndorser Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCK_ENDORSER Role
    - Agent has all the BlockEndorser behaviors
    - Agent has all the BlockEndorser context changes
    """

    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "genesis", 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)

    agent.add_role(agr4bs.roles.StaticPeer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())

    role = agr4bs.models.eth2.roles.BlockEndorser()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_ENDORSER)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BLOCK_ENDORSER) == role


def test_block_endorser_removal():
    """
    Ensures that removing a BlockEndorser Role from an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCK_ENDORSER Role
    - Agent has none of the BlockEndorser behaviors
    - Agent has none of the BlockEndorser context changes
    """
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "genesis", 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    
    agent.add_role(agr4bs.roles.StaticPeer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())

    role = agr4bs.models.eth2.roles.BlockEndorser()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_ENDORSER) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context


def test_block_endorser_reset_attestation_flag_not_attester():
    """
        Ensures that the reset_attestation_flag behavior works as expected

        In all cases, the flag should be reset to False
    """
    network = agr4bs.models.eth2.Factory.build_network(reset=True)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "genesis", 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)
    
    agent.add_role(agr4bs.roles.StaticPeer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())
    agent.add_role(agr4bs.models.eth2.roles.BlockEndorser())

    assert agent.context['attestation_done'] is False

    agent.context['attestation_done'] = True
    assert agent.context['attestation_done'] is True

    agent.reset_attestation_flag(0, [])
    assert agent.context['attestation_done'] is False

    assert network.has_message() is False


def test_block_endorser_reset_attestation_flag_attester():
    """
        Ensures that the reset_attestation_flag behavior works as expected

        In all cases, the flag should be reset to False
        If the agent is part of the attester list for the slot, then a attestation should be
        scheduled when 1/3 of the slot has passed
    """
    network = agr4bs.models.eth2.Factory.build_network(reset=True)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "genesis", 0, [])
    agent = agr4bs.ExternalAgent("agent_0", genesis, agr4bs.models.eth2.Factory)

    date = datetime.datetime(2020, 1, 1, 0, 0, 0)
    agent.init(date)
    
    agent.add_role(agr4bs.roles.StaticPeer())
    agent.add_role(agr4bs.models.eth2.roles.BlockchainMaintainer())
    agent.add_role(agr4bs.models.eth2.roles.BlockEndorser())

    assert agent.context['attestation_done'] is False

    agent.context['attestation_done'] = True
    assert agent.context['attestation_done'] is True

    agent.reset_attestation_flag(0, [agent.name])
    assert agent.context['attestation_done'] is False

    message = network.get_next_message()

    print(message)

    assert isinstance(message, agr4bs.network.messages.RunSchedulable)

    assert message.data[0] == "endorse_block"
    assert message.date == date + datetime.timedelta(seconds=4)
