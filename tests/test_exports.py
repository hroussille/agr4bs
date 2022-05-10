"""
    Test suite for the agr4bs module export structure
"""

from types import ModuleType
import agr4bs


def test_main_module_export():
    """
        Ensures that agr4bs is a module
    """
    assert isinstance(agr4bs, ModuleType)


def test_main_module_agent():
    """
        Ensures that agr4bs exports the Agent class
    """
    assert isinstance(agr4bs.Agent, type)


def test_main_module_role():
    """
        Ensures that agr4bs exports the Role class
    """
    assert isinstance(agr4bs.Role, type)


def test_main_module_group():
    """
        Ensures that agr4bs exports the Group class
    """
    assert isinstance(agr4bs.Group, type)


def test_main_module_block():
    """
        Ensures that agr4bs exports the Block class
    """
    assert isinstance(agr4bs.Block, type)


def test_main_module_transaction():
    """
        Ensures that agr4bs exports the Transaction class
    """
    assert isinstance(agr4bs.Transaction, type)


def test_main_module_payload():
    """
        Ensures that agr4bs exports the Payload class
    """
    assert isinstance(agr4bs.Payload, type)


def test_main_module_investment():
    """
        Ensures that agr4bs exports the Investment class
    """
    assert isinstance(agr4bs.Investment, type)


def test_common_sub_module_export():
    """
        Ensures that agr4bs exports the common submodule
    """
    assert isinstance(agr4bs.common, ModuleType)


def test_groups_sub_module_export():
    """
        Ensures that agr4bs exports the groups submodule
    """
    assert isinstance(agr4bs.groups, ModuleType)


def test_groups_sub_module_interest_group():
    """
        Ensures that agr4bs.groups exports the InterestGroup class
    """
    assert isinstance(agr4bs.groups.InterestGroup, type)


def test_groups_sub_module_structural_group():
    """
        Ensures that agr4bs.groups exports the StructuralGroup class
    """
    assert isinstance(agr4bs.groups.StructuralGroup, type)


def test_roles_sub_module_export():
    """
        Ensures that agr4bs exports the role submodule
    """
    assert isinstance(agr4bs.roles, ModuleType)


def test_roles_sub_module_blockchain_maintainer():
    """
        Ensures that agr4bs.roles exports the BlockchainMaintainer class
    """
    assert isinstance(agr4bs.roles.BlockchainMaintainer, type)


def test_roles_sub_module_block_endorser():
    """
        Ensures that agr4bs.roles exports the BlockEndorser class
    """
    assert isinstance(agr4bs.roles.BlockEndorser, type)


def test_roles_sub_module_block_proposer():
    """
        Ensures that agr4bs.roles exports the BlockProposer class
    """
    assert isinstance(agr4bs.roles.BlockProposer, type)


def test_roles_sub_module_contractor():
    """
        Ensures that agr4bs.roles exports the Contractor class
    """
    assert isinstance(agr4bs.roles.Contractor, type)


def test_roles_sub_module_group_manager():
    """
        Ensures that agr4bs.roles exports the GroupManager class
    """
    assert isinstance(agr4bs.roles.GroupManager, type)


def test_roles_sub_module_investee():
    """
        Ensures that agr4bs.roles exports the Investee class
    """
    assert isinstance(agr4bs.roles.Investee, type)


def test_roles_sub_module_investor():
    """
        Ensures that agr4bs.roles exports the Investor class
    """
    assert isinstance(agr4bs.roles.Investor, type)


def test_roles_sub_module_oracle():
    """
        Ensures that agr4bs.roles exports the Oracle class
    """
    assert isinstance(agr4bs.roles.Oracle, type)


def test_roles_sub_module_transaction_endorser():
    """
        Ensures that agr4bs.roles exports the TransactionEndorser class
    """
    assert isinstance(agr4bs.roles.TransactionEndorser, type)


def test_roles_sub_module_transaction_proposer():
    """
        Ensures that agr4bs.roles exports the TransactionProposer class
    """
    assert isinstance(agr4bs.roles.TransactionProposer, type)
