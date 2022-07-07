
"""
    Test suite for the Receipt class
"""

import pytest
import agr4bs


def test_receipt_properties():
    """
        Test that a Receipt properties can be queried
    """

    tx_hash = "hash"
    state_changes = []
    reverted = False

    receipt = agr4bs.Receipt(tx_hash, state_changes, reverted, "")

    assert receipt.tx_hash == tx_hash
    assert receipt.state_changes == state_changes
    assert receipt.reverted == reverted
    assert receipt.revert_reason == ""


def test_receipt_properties_immutability():
    """
        Test that a Receipt data is immutable
    """

    tx_hash = "hash"
    state_changes = []
    reverted = False

    receipt = agr4bs.Receipt(tx_hash, state_changes, reverted, "")

    with pytest.raises(AttributeError) as excinfo:
        receipt.tx_hash = "fake_hash"
        assert "can't set attribute" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        receipt.state_changes = []
        assert "can't set attribute" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        receipt.reverted = True
        assert "can't set attribute" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        receipt.revert_reason = "some reason"
        assert "can't set attribute" in str(excinfo.value)
