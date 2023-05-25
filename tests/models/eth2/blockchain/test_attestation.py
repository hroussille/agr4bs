
"""
    Test suite for the Attestation class
"""

from agr4bs.models.eth2.blockchain import Attestation


def test_attestation_properties():
    """
        Test that Attestation class exposes the right properties
    """
    attestation = Attestation("agent_0", 0, 0, 0, "genesis", "justified", "first")

    assert attestation.epoch == 0
    assert attestation.slot == 0
    assert attestation.index == 0
    assert attestation.root == "genesis"
    assert attestation.source == "justified"
    assert attestation.target == "first"


def test_attestation_str():
    """
        Test that Attestation class can be printed
    """
    attestation = Attestation("agent_0", 0, 0, 0, "genesis", "justified", "first")

    assert str(attestation) == f"Epoch: {attestation.epoch} Slot: {attestation.slot}, Index: {attestation.index}, Root: {attestation.root}, Source: {attestation.source}, Target: {attestation.target}"

def test_attestation_eq():
    """
        Test that Attestation class can be compared
    """
    attestation1 = Attestation("agent_0", 0, 0, 0, "genesis", "justified", "first")
    attestation2 = Attestation("agent_0", 0, 0, 0, "genesis", "justified", "first")
    attestation3 = Attestation("agent_0", 0, 0, 0, "genesis", "justified", "second")

    assert attestation1 == attestation2
    assert attestation1 != attestation3
    assert attestation2 != attestation3
