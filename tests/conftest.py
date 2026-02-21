"""Shared fixtures for the Simulation Crucible test suite."""

import os
import sys

import pytest

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SCRIPT_DIR = PROJECT_ROOT


@pytest.fixture
def pd_sim():
    """Create a small PrisonersDilemmaSim for testing."""
    from simulations.prisoners_dilemma.simulation import PrisonersDilemmaSim
    return PrisonersDilemmaSim(seed=42, total_rounds=10, num_opponents=3)


@pytest.fixture
def pd_adapter():
    """Create a PrisonersDilemmaAdapter for testing."""
    from simulations.prisoners_dilemma.adapter import PrisonersDilemmaAdapter
    return PrisonersDilemmaAdapter(seed=42, total_rounds=10, num_opponents=3)


@pytest.fixture
def fingerprint():
    """Create a default BehavioralFingerprint."""
    from core.scoring import BehavioralFingerprint
    return BehavioralFingerprint()


@pytest.fixture
def constraint_mgr():
    """Factory fixture for ConstraintManager."""
    from core.constraint_manager import ConstraintManager

    def _make(variant="unconstrained"):
        return ConstraintManager(variant)

    return _make
