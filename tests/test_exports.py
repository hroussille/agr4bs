import agr4bs
from types import ModuleType

def test_main_package_export():
    assert isinstance(agr4bs, ModuleType)

def test_main_package_Agent():
    assert isinstance(agr4bs.Agent, type)

def test_main_package_Role():
    assert isinstance(agr4bs.Role, type)

def test_main_package_Group():
    assert isinstance(agr4bs.Group, type)

def test_main_package_Block():
    assert isinstance(agr4bs.Block, type)

def test_main_package_Transaction():
    assert isinstance(agr4bs.Transaction, type)

def test_main_package_Payload():
    assert isinstance(agr4bs.Payload, type)

def test_main_package_Investment():
    assert isinstance(agr4bs.Investment, type)

def test_common_sub_package_export():
    assert isinstance(agr4bs.Common, ModuleType)

def test_groups_sub_package_export():
    assert isinstance(agr4bs.Groups, ModuleType)

def test_groups_sub_package_InterestGroup():
    assert isinstance(agr4bs.Groups.InterestGroup, type)

def test_groups_sub_package_StructuralGroup():
    assert isinstance(agr4bs.Groups.StructuralGroup, type)
 
def test_roles_sub_package_export():
    assert isinstance(agr4bs.Roles, ModuleType)

def test_roles_sub_package_BlockchainMaintainer():
    assert isinstance(agr4bs.Roles.BlockchainMaintainer, type)

def test_roles_sub_package_BlockEndorser():
    assert isinstance(agr4bs.Roles.BlockEndorser, type)

def test_roles_sub_package_BlockProposer():
    assert isinstance(agr4bs.Roles.BlockProposer, type)

def test_roles_sub_package_Contractor():
    assert isinstance(agr4bs.Roles.Contractor, type)

def test_roles_sub_package_GroupManager():
    assert isinstance(agr4bs.Roles.GroupManager, type)

def test_roles_sub_package_Investee():
    assert isinstance(agr4bs.Roles.Investee, type)

def test_roles_sub_package_Investor():
    assert isinstance(agr4bs.Roles.Investor, type)

def test_roles_sub_package_Oracle():
    assert isinstance(agr4bs.Roles.Oracle, type)

def test_roles_sub_package_TransactionEndorser():
    assert isinstance(agr4bs.Roles.TransactionEndorser, type)

def test_roles_sub_package_TransactionProposer():
    assert isinstance(agr4bs.Roles.TransactionProposer, type)