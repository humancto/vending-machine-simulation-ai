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


# ── Mayor of Splitsville Fixtures ──────────────────────────────────

@pytest.fixture
def ms_sim():
    """Create a MayorSplitsvilleSim for testing (unconstrained)."""
    from simulations.mayor_splitsville.simulation import MayorSplitsvilleSim
    return MayorSplitsvilleSim(seed=42, variant="unconstrained")

@pytest.fixture
def ms_sim_hard():
    """Create a MayorSplitsvilleSim with hard_rules variant."""
    from simulations.mayor_splitsville.simulation import MayorSplitsvilleSim
    return MayorSplitsvilleSim(seed=42, variant="hard_rules")

@pytest.fixture
def ms_adapter():
    """Create a MayorSplitsvilleAdapter for testing."""
    from simulations.mayor_splitsville.adapter import MayorSplitsvilleAdapter
    return MayorSplitsvilleAdapter(seed=42)


# ── Poker Tournament Fixtures ──────────────────────────────────────

@pytest.fixture
def pt_sim():
    """Create a PokerTournamentSim for testing (unconstrained)."""
    from simulations.poker_tournament.simulation import PokerTournamentSim
    return PokerTournamentSim(seed=42, variant="unconstrained")

@pytest.fixture
def pt_sim_hard():
    """Create a PokerTournamentSim with hard_rules variant."""
    from simulations.poker_tournament.simulation import PokerTournamentSim
    return PokerTournamentSim(seed=42, variant="hard_rules")

@pytest.fixture
def pt_adapter():
    """Create a PokerTournamentAdapter for testing."""
    from simulations.poker_tournament.adapter import PokerTournamentAdapter
    return PokerTournamentAdapter(seed=42)


# ── Auction House Fixtures ──────────────────────────────────────────

@pytest.fixture
def ah_sim():
    """Create an AuctionHouseSim for testing (unconstrained)."""
    from simulations.auction_house.simulation import AuctionHouseSim
    return AuctionHouseSim(seed=42, variant="unconstrained")

@pytest.fixture
def ah_sim_hard():
    """Create an AuctionHouseSim with hard_rules variant."""
    from simulations.auction_house.simulation import AuctionHouseSim
    return AuctionHouseSim(seed=42, variant="hard_rules")

@pytest.fixture
def ah_adapter():
    """Create an AuctionHouseAdapter for testing."""
    from simulations.auction_house.adapter import AuctionHouseAdapter
    return AuctionHouseAdapter(seed=42)


# ── Resource Commons Fixtures ─────────────────────────────────────────

@pytest.fixture
def rc_sim():
    """Create a ResourceCommonsSim for testing (unconstrained)."""
    from simulations.resource_commons.simulation import ResourceCommonsSim
    return ResourceCommonsSim(seed=42, total_seasons=30, variant="unconstrained")

@pytest.fixture
def rc_sim_hard():
    """Create a ResourceCommonsSim with hard_rules variant."""
    from simulations.resource_commons.simulation import ResourceCommonsSim
    return ResourceCommonsSim(seed=42, total_seasons=30, variant="hard_rules")

@pytest.fixture
def rc_adapter():
    """Create a ResourceCommonsAdapter for testing."""
    from simulations.resource_commons.adapter import ResourceCommonsAdapter
    return ResourceCommonsAdapter(seed=42)


# -- Asteroid Defense Fixtures ────────────────────────────────────────

@pytest.fixture
def ad_sim():
    """Create an AsteroidDefenseSim for testing (unconstrained)."""
    from simulations.asteroid_defense.simulation import AsteroidDefenseSim
    return AsteroidDefenseSim(seed=42, total_months=36, variant="unconstrained")

@pytest.fixture
def ad_sim_hard():
    """Create an AsteroidDefenseSim with hard_rules variant."""
    from simulations.asteroid_defense.simulation import AsteroidDefenseSim
    return AsteroidDefenseSim(seed=42, total_months=36, variant="hard_rules")

@pytest.fixture
def ad_adapter():
    """Create an AsteroidDefenseAdapter for testing."""
    from simulations.asteroid_defense.adapter import AsteroidDefenseAdapter
    return AsteroidDefenseAdapter(seed=42)


# ── Pandemic Ward Fixtures ──────────────────────────────────────────

@pytest.fixture
def pw_sim():
    """Create a PandemicWardSim for testing (unconstrained)."""
    from simulations.pandemic_ward.simulation import PandemicWardSim
    return PandemicWardSim(seed=42, total_days=90, variant="unconstrained")

@pytest.fixture
def pw_sim_hard():
    """Create a PandemicWardSim with hard_rules variant."""
    from simulations.pandemic_ward.simulation import PandemicWardSim
    return PandemicWardSim(seed=42, total_days=90, variant="hard_rules")

@pytest.fixture
def pw_adapter():
    """Create a PandemicWardAdapter for testing."""
    from simulations.pandemic_ward.adapter import PandemicWardAdapter
    return PandemicWardAdapter(seed=42, total_days=90, variant="unconstrained")


# ── Species Triage Fixtures ─────────────────────────────────────────

@pytest.fixture
def st_sim():
    """Create a SpeciesTriageSim for testing (unconstrained)."""
    from simulations.species_triage.simulation import SpeciesTriageSim
    return SpeciesTriageSim(seed=42, total_quarters=40, variant="unconstrained")

@pytest.fixture
def st_sim_hard():
    """Create a SpeciesTriageSim with hard_rules variant."""
    from simulations.species_triage.simulation import SpeciesTriageSim
    return SpeciesTriageSim(seed=42, total_quarters=40, variant="hard_rules")

@pytest.fixture
def st_adapter():
    """Create a SpeciesTriageAdapter for testing."""
    from simulations.species_triage.adapter import SpeciesTriageAdapter
    return SpeciesTriageAdapter(seed=42)


# ── Supply Chain Fixtures ─────────────────────────────────────────────

@pytest.fixture
def sc_sim():
    """Create a SupplyChainSim for testing (unconstrained)."""
    from simulations.supply_chain.simulation import SupplyChainSim
    return SupplyChainSim(seed=42, total_weeks=52, variant="unconstrained")

@pytest.fixture
def sc_sim_hard():
    """Create a SupplyChainSim with hard_rules variant."""
    from simulations.supply_chain.simulation import SupplyChainSim
    return SupplyChainSim(seed=42, total_weeks=52, variant="hard_rules")

@pytest.fixture
def sc_adapter():
    """Create a SupplyChainAdapter for testing."""
    from simulations.supply_chain.adapter import SupplyChainAdapter
    return SupplyChainAdapter(seed=42)


# ── News Editor Fixtures ─────────────────────────────────────────────
@pytest.fixture
def ne_sim():
    from simulations.news_editor.simulation import NewsEditorSim
    return NewsEditorSim(seed=42, total_hours=48, variant="unconstrained")

@pytest.fixture
def ne_sim_hard():
    from simulations.news_editor.simulation import NewsEditorSim
    return NewsEditorSim(seed=42, total_hours=48, variant="hard_rules")

@pytest.fixture
def ne_adapter():
    from simulations.news_editor.adapter import NewsEditorAdapter
    return NewsEditorAdapter(seed=42)


# ── Nuclear Launch Fixtures ─────────────────────────────────────────────

@pytest.fixture
def nl_sim():
    """Create a NuclearLaunchSim for testing (unconstrained)."""
    from simulations.nuclear_launch.simulation import NuclearLaunchSim
    return NuclearLaunchSim(seed=42, total_hours=24, variant="unconstrained")

@pytest.fixture
def nl_sim_hard():
    """Create a NuclearLaunchSim with hard_rules variant."""
    from simulations.nuclear_launch.simulation import NuclearLaunchSim
    return NuclearLaunchSim(seed=42, total_hours=24, variant="hard_rules")

@pytest.fixture
def nl_adapter():
    """Create a NuclearLaunchAdapter for testing."""
    from simulations.nuclear_launch.adapter import NuclearLaunchAdapter
    return NuclearLaunchAdapter(seed=42, total_hours=24, variant="unconstrained")


# ── Last Restaurant Fixtures ─────────────────────────────────────────
@pytest.fixture
def lr_sim():
    from simulations.last_restaurant.simulation import LastRestaurantSim
    return LastRestaurantSim(seed=42, total_weeks=52, variant="unconstrained")

@pytest.fixture
def lr_sim_hard():
    from simulations.last_restaurant.simulation import LastRestaurantSim
    return LastRestaurantSim(seed=42, total_weeks=52, variant="hard_rules")

@pytest.fixture
def lr_adapter():
    from simulations.last_restaurant.adapter import LastRestaurantAdapter
    return LastRestaurantAdapter(seed=42)


# ── Flash Crash Fixtures ─────────────────────────────────────────────
@pytest.fixture
def fc_sim():
    from simulations.flash_crash.simulation import FlashCrashSim
    return FlashCrashSim(seed=42, total_hours=120, variant="unconstrained")

@pytest.fixture
def fc_sim_hard():
    from simulations.flash_crash.simulation import FlashCrashSim
    return FlashCrashSim(seed=42, total_hours=120, variant="hard_rules")

@pytest.fixture
def fc_adapter():
    from simulations.flash_crash.adapter import FlashCrashAdapter
    return FlashCrashAdapter(seed=42)


# ── Real Estate Empire Fixtures ─────────────────────────────────────

@pytest.fixture
def re2_sim():
    """Create a RealEstateSim for testing (unconstrained)."""
    from simulations.real_estate.simulation import RealEstateSim
    return RealEstateSim(seed=42, total_months=36, variant="unconstrained")

@pytest.fixture
def re2_sim_hard():
    """Create a RealEstateSim with hard_rules variant."""
    from simulations.real_estate.simulation import RealEstateSim
    return RealEstateSim(seed=42, total_months=36, variant="hard_rules")

@pytest.fixture
def re2_adapter():
    """Create a RealEstateAdapter for testing."""
    from simulations.real_estate.adapter import RealEstateAdapter
    return RealEstateAdapter(seed=42)


# ── Startup Founder Fixtures ─────────────────────────────────────────

@pytest.fixture
def sf_sim():
    """Create a StartupFounderSim for testing (unconstrained)."""
    from simulations.startup_founder.simulation import StartupFounderSim
    return StartupFounderSim(seed=42, total_months=24, variant="unconstrained")

@pytest.fixture
def sf_sim_hard():
    """Create a StartupFounderSim with hard_rules variant."""
    from simulations.startup_founder.simulation import StartupFounderSim
    return StartupFounderSim(seed=42, total_months=24, variant="hard_rules")

@pytest.fixture
def sf_adapter():
    """Create a StartupFounderAdapter for testing."""
    from simulations.startup_founder.adapter import StartupFounderAdapter
    return StartupFounderAdapter(seed=42)


# ── Experimental Treatment Fixtures ──────────────────────────────────
@pytest.fixture
def et_sim():
    from simulations.experimental_treatment.simulation import ExperimentalTreatmentSim
    return ExperimentalTreatmentSim(seed=42, total_months=18, variant="unconstrained")

@pytest.fixture
def et_sim_hard():
    from simulations.experimental_treatment.simulation import ExperimentalTreatmentSim
    return ExperimentalTreatmentSim(seed=42, total_months=18, variant="hard_rules")

@pytest.fixture
def et_adapter():
    from simulations.experimental_treatment.adapter import ExperimentalTreatmentAdapter
    return ExperimentalTreatmentAdapter(seed=42)


# ── Organ Allocation Fixtures ────────────────────────────────────────

@pytest.fixture
def oa_sim():
    """Create an OrganAllocationSim for testing (unconstrained)."""
    from simulations.organ_allocation.simulation import OrganAllocationSim
    return OrganAllocationSim(seed=42, total_weeks=52, variant="unconstrained")

@pytest.fixture
def oa_sim_hard():
    """Create an OrganAllocationSim with hard_rules variant."""
    from simulations.organ_allocation.simulation import OrganAllocationSim
    return OrganAllocationSim(seed=42, total_weeks=52, variant="hard_rules")

@pytest.fixture
def oa_adapter():
    """Create an OrganAllocationAdapter for testing."""
    from simulations.organ_allocation.adapter import OrganAllocationAdapter
    return OrganAllocationAdapter(seed=42)


# ── Pandemic Grand Strategy Fixtures ──────────────────────────────────

@pytest.fixture
def pg_sim():
    from simulations.pandemic_grand.simulation import PandemicGrandSim
    return PandemicGrandSim(seed=42, total_months=24)

@pytest.fixture
def pg_sim_hard():
    from simulations.pandemic_grand.simulation import PandemicGrandSim
    return PandemicGrandSim(seed=42, total_months=24, variant="hard_rules")

@pytest.fixture
def pg_adapter():
    from simulations.pandemic_grand.adapter import PandemicGrandAdapter
    return PandemicGrandAdapter(seed=42, total_months=24)


# ── Intelligence Mosaic Fixtures ──────────────────────────────────────

@pytest.fixture
def im_sim():
    from simulations.intelligence_mosaic.simulation import IntelligenceMosaicSim
    return IntelligenceMosaicSim(seed=42, total_days=30)

@pytest.fixture
def im_sim_hard():
    from simulations.intelligence_mosaic.simulation import IntelligenceMosaicSim
    return IntelligenceMosaicSim(seed=42, total_days=30, variant="hard_rules")

@pytest.fixture
def im_adapter():
    from simulations.intelligence_mosaic.adapter import IntelligenceMosaicAdapter
    return IntelligenceMosaicAdapter(seed=42, total_days=30)


# ── Drone Strike Fixtures ─────────────────────────────────────────────

@pytest.fixture
def ds_sim():
    """Create a DroneStrikeSim for testing (unconstrained)."""
    from simulations.drone_strike.simulation import DroneStrikeSim
    return DroneStrikeSim(seed=42, total_hours=48, variant="unconstrained")

@pytest.fixture
def ds_sim_hard():
    """Create a DroneStrikeSim with hard_rules variant."""
    from simulations.drone_strike.simulation import DroneStrikeSim
    return DroneStrikeSim(seed=42, total_hours=48, variant="hard_rules")

@pytest.fixture
def ds_adapter():
    """Create a DroneStrikeAdapter for testing."""
    from simulations.drone_strike.adapter import DroneStrikeAdapter
    return DroneStrikeAdapter(seed=42, total_hours=48, variant="unconstrained")


# ── POW Camp Commander Fixtures ──────────────────────────────────────

@pytest.fixture
def pc_sim():
    from simulations.pow_camp.simulation import POWCampSim
    return POWCampSim(seed=42)

@pytest.fixture
def pc_sim_hard():
    from simulations.pow_camp.simulation import POWCampSim
    return POWCampSim(seed=42, variant="hard_rules")

@pytest.fixture
def pc_adapter():
    from simulations.pow_camp.adapter import POWCampAdapter
    return POWCampAdapter(seed=42)
