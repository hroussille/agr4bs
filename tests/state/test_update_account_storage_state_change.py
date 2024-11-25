
"""
    Test suite for the UpdateAccountStorage StateChange class
"""

from deepdiff import DeepDiff, Delta
from agr4bs.state import UpdateAccountStorage
from agr4bs.state.state_change import StateChangeType


def test_update_account_storage_state_change_type():
    """
        Test that an UpdateAccountStorage StateChange has the given type
    """
    storage_before = {}
    storage_after = {"key": "value"}

    delta_apply = Delta(DeepDiff(storage_before, storage_after))
    delta_revert = Delta(DeepDiff(storage_after, storage_before))

    change = UpdateAccountStorage("account_name", delta_apply, delta_revert)

    assert change.type == StateChangeType.UPDATE_ACCOUNT_STORAGE


def test_update_account_storage_state_change_properties():
    """
        Test that the properties of an UpdateAccountStorage
         StateChangee are all present and accessibles.
    """
    storage_before = {}
    storage_after = {"key": "value"}

    delta_apply = Delta(DeepDiff(storage_before, storage_after))
    delta_revert = Delta(DeepDiff(storage_after, storage_before))

    change = UpdateAccountStorage("account_name", delta_apply, delta_revert)

    assert change.account_name == "account_name"
    assert change.delta_apply == delta_apply
    assert change.delta_revert == delta_revert

    assert storage_before + change.delta_apply == storage_after


def test_update_account_storage_state_change_revert():
    """
        Test that reverting an UpdateAccountStorage StateChange yields an
        UpdateAccountStorage StateChange with inverted deltas
    """

    storage_before = {}
    storage_after = {"key": "value"}

    delta_apply = Delta(DeepDiff(storage_before, storage_after))
    delta_revert = Delta(DeepDiff(storage_after, storage_before))

    change = UpdateAccountStorage("account_name", delta_apply, delta_revert)
    reverted = change.revert()

    assert storage_after + reverted.delta_apply == storage_before
