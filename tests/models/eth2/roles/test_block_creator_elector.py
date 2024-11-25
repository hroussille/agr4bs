"""
    Test suite for the BlockCreatorElector Role
"""

import datetime
import agr4bs


def test_block_creator_elector():
    """
    Ensures that a BlockCreatorElector has the appropriate RoleType
    """
    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    assert role.type == agr4bs.RoleType.BLOCK_CREATOR_ELECTOR


def test_block_creator_elector_behaviors():
    """
    Ensures that a BlockCreatorElector  has the appropriate behaviors :
    """
    role = agr4bs.models.eth2.roles.BlockCreatorElector()

    assert 'next_epoch' in role.behaviors
    assert 'next_slot' in role.behaviors
    assert 'context_change' not in role.behaviors


def test_block_creator_elector_addition():
    """
    Ensures that adding a BlockCreatorElector Role to an Agent leads
    to the appropriate behavior :

    - Agent has the BLOCK_CREATOR_ELECTOR Role
    - Agent has all the BLOCK_CREATOR_ELECTOR behaviors
    - Agent has all the BLOCK_CREATOR_ELECTOR context changes
    """
    agent = agr4bs.Environment(agr4bs.models.eth2.Factory)
    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    agent.add_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_CREATOR_ELECTOR)

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior)

    for context_change in role.context_change().mount():
        assert context_change in agent.context

    assert agent.get_role(agr4bs.RoleType.BLOCK_CREATOR_ELECTOR) == role


def test_block_creator_elector_removal():
    """
    Ensures that removing a BlockCreatorElector Role to an Agent leads
    to the appropriate behavior :

    - Agent doesn't have the BLOCK_CREATOR_ELECTOR Role
    - Agent has none of the BlockCreatorElector behaviors
    - Agent has none of the BlockCreatorElector context changes
    """
    agent = agr4bs.Agent("agent_0", agr4bs.AgentType.EXTERNAL_AGENT)
    role = agr4bs.models.eth2.roles.BlockCreatorElector()

    agent.add_role(role)
    agent.remove_role(role)

    assert agent.has_role(agr4bs.RoleType.BLOCK_CREATOR_ELECTOR) is False

    for behavior in role.behaviors:
        assert agent.has_behavior(behavior) is False

    for context_change in role.context_change().mount():
        assert context_change not in agent.context

def test_block_creator_elector_initialize():
    """
    Ensures that the initialize behavior of a BlockCreatorElector Role
    works as expected
    """
    environment = agr4bs.Environment(agr4bs.models.eth2.Factory)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "environment", 0, [])
    factory = agr4bs.models.eth2.Factory


    for i in range(32):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, factory)
        environment.add_agent(agent)


    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    environment.add_role(role)
    date = datetime.datetime(2020, 1, 1, 0, 0, 0)

    # Initial epoch is -1 : the environment will init and move to epoch 0
    assert environment.context['epoch'] == -1
    assert environment.context['slot'] == 0

    environment.init(date)

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 0

    assert len(environment.context['block_proposers']) == 32
    assert len(environment.context['block_attesters']) == 32

    attesters = []

    for i in range(32):
        attesters = attesters + environment.context['block_attesters'][i]

    attesters = set(attesters)

    assert len(attesters) == len(environment.agents_names)

    for agent_name in environment.agents_names:
        assert agent_name in attesters
    

def test_block_creator_elector_next_epoch():
    """
    Ensures that the next_epoch behavior of a BlockCreatorElector Role
    works as expected
    """
    environment = agr4bs.Environment(agr4bs.models.eth2.Factory)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "environment", 0, [])
    factory = agr4bs.models.eth2.Factory


    for i in range(32):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, factory)
        environment.add_agent(agent)


    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    environment.add_role(role)
    date = datetime.datetime(2020, 1, 1, 0, 0, 0)

    environment.init(date)

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 0

    environment.next_epoch()

    assert environment.context['epoch'] == 1
    assert environment.context['slot'] == 0

def test_block_creator_elector_next_slot():
    """
    Ensures that the next_slot behavior of a BlockCreatorElector Role
    works as expected
    """
    environment = agr4bs.Environment(agr4bs.models.eth2.Factory)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "environment", 0, [])
    factory = agr4bs.models.eth2.Factory


    for i in range(32):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, factory)
        environment.add_agent(agent)


    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    environment.add_role(role)
    date = datetime.datetime(2020, 1, 1, 0, 0, 0)

    environment.init(date)

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 0

    environment.next_slot()

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 1



def test_block_creator_elector_next_slot_next_epoch():
    """
    Ensures that the next_slot behavior of a BlockCreatorElector Role
    works as expected when moving to the next slot leads to a new epoch
    """
    environment = agr4bs.Environment(agr4bs.models.eth2.Factory)
    genesis = agr4bs.models.eth2.blockchain.Block("genesis", "environment", 0, [])
    factory = agr4bs.models.eth2.Factory


    for i in range(32):
        agent = agr4bs.ExternalAgent(f"agent_{i}", genesis, factory)
        environment.add_agent(agent)


    role = agr4bs.models.eth2.roles.BlockCreatorElector()
    environment.add_role(role)
    date = datetime.datetime(2020, 1, 1, 0, 0, 0)


    assert environment.context['epoch'] == -1
    assert environment.context['slot'] == 0

    environment.init(date)

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 0

    # Force the environment to be in slot 31
    environment.context['slot'] = 31

    assert environment.context['epoch'] == 0
    assert environment.context['slot'] == 31

    environment.next_slot()

    assert environment.context['epoch'] == 1
    assert environment.context['slot'] == 32
