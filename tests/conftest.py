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


# ── Emergency Room Fixtures ──────────────────────────────────────────

@pytest.fixture
def er_sim():
    """Create an EmergencyRoomSim for testing (unconstrained)."""
    from simulations.emergency_room.simulation import EmergencyRoomSim
    return EmergencyRoomSim(seed=42, total_hours=72, variant="unconstrained")


@pytest.fixture
def er_adapter():
    """Create an EmergencyRoomAdapter for testing."""
    from simulations.emergency_room.adapter import EmergencyRoomAdapter
    return EmergencyRoomAdapter(seed=42, total_hours=72, variant="unconstrained")


@pytest.fixture
def er_sim_hard():
    """Create an EmergencyRoomSim with hard_rules variant."""
    from simulations.emergency_room.simulation import EmergencyRoomSim
    return EmergencyRoomSim(seed=42, total_hours=72, variant="hard_rules")


# ── Corporate Whistleblower Fixtures ─────────────────────────────────

@pytest.fixture
def wb_sim():
    """Create a WhistleblowerSim for testing (unconstrained)."""
    from simulations.whistleblower.simulation import WhistleblowerSim
    return WhistleblowerSim(seed=42, total_weeks=8, variant="unconstrained")


@pytest.fixture
def wb_adapter():
    """Create a WhistleblowerAdapter for testing."""
    from simulations.whistleblower.adapter import WhistleblowerAdapter
    return WhistleblowerAdapter(seed=42, total_weeks=8, variant="unconstrained")


@pytest.fixture
def wb_sim_hard():
    """Create a WhistleblowerSim with hard_rules variant."""
    from simulations.whistleblower.simulation import WhistleblowerSim
    return WhistleblowerSim(seed=42, total_weeks=8, variant="hard_rules")


# ── Content Moderator Fixtures ───────────────────────────────────────

@pytest.fixture
def cm_sim():
    from simulations.content_moderator.simulation import ContentModeratorSim
    return ContentModeratorSim(seed=42, total_hours=48, variant="unconstrained")

@pytest.fixture
def cm_adapter():
    from simulations.content_moderator.adapter import ContentModeratorAdapter
    return ContentModeratorAdapter(seed=42, total_hours=48, variant="unconstrained")

@pytest.fixture
def cm_sim_hard():
    from simulations.content_moderator.simulation import ContentModeratorSim
    return ContentModeratorSim(seed=42, total_hours=48, variant="hard_rules")


# ── Rules of Engagement Fixtures ─────────────────────────────────────

@pytest.fixture
def roe_sim():
    from simulations.rules_of_engagement.simulation import RulesOfEngagementSim
    return RulesOfEngagementSim(seed=42, total_hours=72, variant="unconstrained")

@pytest.fixture
def roe_sim_hard():
    from simulations.rules_of_engagement.simulation import RulesOfEngagementSim
    return RulesOfEngagementSim(seed=42, total_hours=72, variant="hard_rules")

@pytest.fixture
def roe_adapter():
    from simulations.rules_of_engagement.adapter import RulesOfEngagementAdapter
    return RulesOfEngagementAdapter(seed=42, total_hours=72, variant="unconstrained")


# ── Reputation Economy Fixtures ─────────────────────────────────────

@pytest.fixture
def re_sim():
    from simulations.reputation_economy.simulation import ReputationEconomySim
    return ReputationEconomySim(seed=42, total_days=60, variant="unconstrained")

@pytest.fixture
def re_sim_hard():
    from simulations.reputation_economy.simulation import ReputationEconomySim
    return ReputationEconomySim(seed=42, total_days=60, variant="hard_rules")

@pytest.fixture
def re_adapter():
    from simulations.reputation_economy.adapter import ReputationEconomyAdapter
    return ReputationEconomyAdapter(seed=42)


# ── Drug Pricing Fixtures ─────────────────────────────────────────────

@pytest.fixture
def dp_sim():
    """Create a DrugPricingSim for testing (unconstrained)."""
    from simulations.drug_pricing.simulation import DrugPricingSim
    return DrugPricingSim(seed=42, variant="unconstrained")

@pytest.fixture
def dp_sim_hard():
    """Create a DrugPricingSim with hard_rules variant."""
    from simulations.drug_pricing.simulation import DrugPricingSim
    return DrugPricingSim(seed=42, variant="hard_rules")

@pytest.fixture
def dp_adapter():
    """Create a DrugPricingAdapter for testing."""
    from simulations.drug_pricing.adapter import DrugPricingAdapter
    return DrugPricingAdapter(seed=42)
