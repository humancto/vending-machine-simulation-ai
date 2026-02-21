"""Tests for simulations/asteroid_defense/models.py."""

import pytest
from simulations.asteroid_defense.models import (
    NationId, DeflectionStrategy, CrisisType, DilemmaType,
    Nation, DeflectionPlan, BillionaireOffer, CrisisEvent,
    EthicalDilemma, TrajectoryData, VisibleMetrics,
)


class TestEnums:

    def test_nation_id_values(self):
        assert NationId.US.value == "us"
        assert NationId.CHINA.value == "china"
        assert NationId.NIGERIA.value == "nigeria"

    def test_nation_id_count(self):
        assert len(NationId) == 12

    def test_deflection_strategy_values(self):
        assert DeflectionStrategy.KINETIC_IMPACTOR.value == "kinetic_impactor"
        assert DeflectionStrategy.NUCLEAR.value == "nuclear"

    def test_deflection_strategy_count(self):
        assert len(DeflectionStrategy) == 5

    def test_crisis_type_values(self):
        assert CrisisType.TRAJECTORY_UPDATE.value == "trajectory_update"
        assert CrisisType.TECH_FAILURE.value == "tech_failure"

    def test_crisis_type_count(self):
        assert len(CrisisType) == 8

    def test_dilemma_type_values(self):
        assert DilemmaType.BILLIONAIRE_OFFER.value == "billionaire_offer"
        assert DilemmaType.MARTIAL_LAW.value == "martial_law"

    def test_dilemma_type_count(self):
        assert len(DilemmaType) == 12


class TestNation:

    def test_nation_creation(self):
        n = Nation(
            nation_id=NationId.US,
            name="United States",
            gdp_contribution=25.0,
            tech_capability=95.0,
            political_stability=70.0,
            population_millions=335.0,
        )
        assert n.name == "United States"
        assert n.gdp_contribution == 25.0
        assert n.cooperation_level == 50.0  # default
        assert n.satisfaction == 50.0  # default
        assert n.is_developing is False

    def test_nation_developing_flag(self):
        n = Nation(
            nation_id=NationId.NIGERIA,
            name="Nigeria",
            gdp_contribution=1.5,
            tech_capability=25.0,
            political_stability=40.0,
            population_millions=220.0,
            is_developing=True,
        )
        assert n.is_developing is True


class TestDeflectionPlan:

    def test_plan_creation(self):
        p = DeflectionPlan(
            strategy=DeflectionStrategy.KINETIC_IMPACTOR,
            name="DART-II",
            description="Kinetic impactor",
            cost_billions=15.0,
            timeline_months=18,
            success_probability=0.65,
            risk_level=0.15,
            nations_required=3,
        )
        assert p.cost_billions == 15.0
        assert p.funded is False
        assert p.active is False
        assert p.deployed is False


class TestBillionaireOffer:

    def test_offer_creation(self):
        b = BillionaireOffer(
            offer_id="test_01",
            month=4,
            name="Test Billionaire",
            description="Test offer",
            funding_amount=8.0,
            strings_attached="naming rights",
        )
        assert b.funding_amount == 8.0
        assert b.accepted is False
        assert b.rejected is False
        assert b.presented is False


class TestTrajectoryData:

    def test_trajectory_creation(self):
        t = TrajectoryData(
            impact_probability=0.15,
            estimated_impact_date="Month 36",
            uncertainty_range_km=500.0,
        )
        assert t.impact_probability == 0.15
        assert t.deflection_progress == 0.0
        assert t.fragments_detected == 0


class TestVisibleMetrics:

    def test_default_metrics(self):
        m = VisibleMetrics()
        assert m.deflection_progress == 0.0
        assert m.total_funding_billions == 0.0
        assert m.global_cooperation == 50.0
        assert m.public_confidence == 50.0
        assert m.scientific_readiness == 30.0
        assert m.political_support == 50.0
        assert m.months_remaining == 36
        assert m.impact_probability == 15.0
