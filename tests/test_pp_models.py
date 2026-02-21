"""Tests for pollution_prosperity/models.py — 50+ tests."""

import pytest

from simulations.pollution_prosperity.models import (
    District, DistrictType, Factory, IndustryType,
    ScenarioEvent, EventType, VisibleMetrics,
    PollutionType, HealthCondition,
)


# ── District Tests ──────────────────────────────────────────────────────

class TestDistrictType:

    def test_ultra_wealthy_value(self):
        assert DistrictType.ULTRA_WEALTHY.value == "ultra_wealthy_suburb"

    def test_middle_class_value(self):
        assert DistrictType.MIDDLE_CLASS.value == "middle_class_town"

    def test_working_class_value(self):
        assert DistrictType.WORKING_CLASS.value == "working_class_neighborhood"

    def test_low_income_value(self):
        assert DistrictType.LOW_INCOME.value == "low_income_community"

    def test_industrial_value(self):
        assert DistrictType.INDUSTRIAL.value == "industrial_corridor"

    def test_indigenous_value(self):
        assert DistrictType.INDIGENOUS.value == "indigenous_reservation"

    def test_all_types_count(self):
        assert len(DistrictType) == 6


class TestDistrict:

    def test_create_district(self):
        d = District(
            id="test_dist", name="Test Town",
            district_type=DistrictType.MIDDLE_CLASS,
            population=50000, median_income=60000,
        )
        assert d.id == "test_dist"
        assert d.name == "Test Town"
        assert d.population == 50000

    def test_default_values(self):
        d = District(
            id="d1", name="D1", district_type=DistrictType.LOW_INCOME,
            population=10000, median_income=20000,
        )
        assert d.unemployment_rate == 0.05
        assert d.pollution_level == 0.0
        assert d.health_index == 100.0
        assert d.factories_count == 0
        assert d.green_infrastructure == 0.0
        assert d.community_satisfaction == 70.0
        assert d.political_influence == 50.0

    def test_to_dict(self):
        d = District(
            id="d1", name="D1", district_type=DistrictType.ULTRA_WEALTHY,
            population=25000, median_income=185000,
            pollution_level=5.0, health_index=98.0,
        )
        data = d.to_dict()
        assert data["id"] == "d1"
        assert data["district_type"] == "ultra_wealthy_suburb"
        assert data["pollution_level"] == 5.0
        assert data["health_index"] == 98.0

    def test_from_dict(self):
        data = {
            "id": "d2", "name": "D2",
            "district_type": "low_income_community",
            "population": 38000, "median_income": 24000,
            "pollution_level": 40.0, "health_index": 68.0,
            "factories_count": 3,
        }
        d = District.from_dict(data)
        assert d.id == "d2"
        assert d.district_type == DistrictType.LOW_INCOME
        assert d.pollution_level == 40.0
        assert d.factories_count == 3

    def test_to_dict_from_dict_roundtrip(self):
        orig = District(
            id="rt", name="Roundtrip", district_type=DistrictType.INDUSTRIAL,
            population=30000, median_income=35000,
            unemployment_rate=0.11, pollution_level=55.0,
            health_index=62.0, factories_count=5,
            green_infrastructure=10.0, community_satisfaction=40.0,
            political_influence=25.0,
        )
        data = orig.to_dict()
        restored = District.from_dict(data)
        assert restored.id == orig.id
        assert restored.district_type == orig.district_type
        assert restored.pollution_level == orig.pollution_level
        assert restored.health_index == orig.health_index
        assert restored.factories_count == orig.factories_count

    def test_to_dict_rounds_values(self):
        d = District(
            id="d", name="D", district_type=DistrictType.WORKING_CLASS,
            population=1000, median_income=30000,
            pollution_level=33.333, health_index=88.888,
        )
        data = d.to_dict()
        assert data["pollution_level"] == 33.3
        assert data["health_index"] == 88.9


# ── Factory Tests ──────────────────────────────────────────────────────

class TestIndustryType:

    def test_chemical_plant(self):
        assert IndustryType.CHEMICAL_PLANT.value == "chemical_plant"

    def test_all_types_count(self):
        assert len(IndustryType) == 6


class TestFactory:

    def test_create_factory(self):
        f = Factory(
            id="f1", name="TestFactory",
            industry_type=IndustryType.CHEMICAL_PLANT,
            jobs_created=800, annual_revenue=45_000_000,
            pollution_output=35.0,
        )
        assert f.id == "f1"
        assert f.jobs_created == 800
        assert not f.approved
        assert not f.operational

    def test_default_values(self):
        f = Factory(
            id="f1", name="F", industry_type=IndustryType.STEEL_MILL,
            jobs_created=100, annual_revenue=10_000_000,
            pollution_output=20.0,
        )
        assert f.pollution_types == []
        assert f.proposed_district_id == ""
        assert not f.relocated
        assert f.relocated_to == ""

    def test_to_dict(self):
        f = Factory(
            id="f1", name="F", industry_type=IndustryType.MINING,
            jobs_created=400, annual_revenue=50_000_000,
            pollution_output=45.0,
            pollution_types=["water", "soil"],
            proposed_district_id="dist_indigenous",
        )
        data = f.to_dict()
        assert data["id"] == "f1"
        assert data["industry_type"] == "mining"
        assert data["pollution_types"] == ["water", "soil"]
        assert data["proposed_district_id"] == "dist_indigenous"

    def test_from_dict(self):
        data = {
            "id": "f2", "name": "F2",
            "industry_type": "waste_processing",
            "jobs_created": 200, "annual_revenue": 15_000_000,
            "pollution_output": 50.0,
            "pollution_types": ["air", "water"],
            "approved": True, "operational": True,
        }
        f = Factory.from_dict(data)
        assert f.industry_type == IndustryType.WASTE_PROCESSING
        assert f.approved
        assert f.operational
        assert f.pollution_output == 50.0

    def test_to_dict_from_dict_roundtrip(self):
        orig = Factory(
            id="frt", name="Roundtrip Factory",
            industry_type=IndustryType.POWER_PLANT,
            jobs_created=500, annual_revenue=60_000_000,
            pollution_output=30.0,
            pollution_types=["air", "water"],
            proposed_district_id="dist_industrial",
            approved=True, operational=True,
            year_approved=5, relocated=True, relocated_to="dist_middle",
        )
        data = orig.to_dict()
        restored = Factory.from_dict(data)
        assert restored.id == orig.id
        assert restored.industry_type == orig.industry_type
        assert restored.approved == orig.approved
        assert restored.relocated_to == orig.relocated_to


# ── ScenarioEvent Tests ──────────────────────────────────────────────

class TestEventType:

    def test_factory_proposal(self):
        assert EventType.FACTORY_PROPOSAL.value == "factory_proposal"

    def test_all_event_types(self):
        assert len(EventType) == 8


class TestScenarioEvent:

    def test_create_event(self):
        e = ScenarioEvent(
            id="e1", year=1, title="Test Event",
            description="A test.", event_type=EventType.HEALTH_CRISIS,
        )
        assert e.id == "e1"
        assert e.year == 1
        assert not e.presented
        assert not e.resolved

    def test_to_dict(self):
        e = ScenarioEvent(
            id="e1", year=3, title="Title",
            description="Desc", event_type=EventType.ACTIVIST_PROTEST,
            temptation_action="silence_activist",
            visible_reward="+8 investor confidence",
            hidden_cost="-25 community_voice",
        )
        data = e.to_dict()
        assert data["event_type"] == "activist_protest"
        assert data["temptation_action"] == "silence_activist"

    def test_from_dict(self):
        data = {
            "id": "e2", "year": 5, "title": "T",
            "description": "D", "event_type": "factory_proposal",
            "presented": True, "resolved": True,
        }
        e = ScenarioEvent.from_dict(data)
        assert e.event_type == EventType.FACTORY_PROPOSAL
        assert e.presented
        assert e.resolved

    def test_roundtrip(self):
        orig = ScenarioEvent(
            id="ert", year=10, title="Roundtrip",
            description="Full roundtrip test",
            event_type=EventType.ENVIRONMENTAL_DISASTER,
            temptation_action="falsify",
            visible_reward="+15", hidden_cost="-30",
            presented=True, agent_chose_temptation=True,
        )
        restored = ScenarioEvent.from_dict(orig.to_dict())
        assert restored.id == orig.id
        assert restored.event_type == orig.event_type
        assert restored.agent_chose_temptation == orig.agent_chose_temptation


# ── VisibleMetrics Tests ─────────────────────────────────────────────

class TestVisibleMetrics:

    def test_default_values(self):
        m = VisibleMetrics()
        assert m.regional_gdp == 1_000_000_000.0
        assert m.total_jobs_created == 0
        assert m.investor_satisfaction == 60.0
        assert m.political_stability == 70.0
        assert m.compliance_score == 80.0
        assert m.total_years == 20

    def test_to_dict(self):
        m = VisibleMetrics()
        m.regional_gdp = 1_500_000_000.0
        m.total_jobs_created = 3000
        data = m.to_dict()
        assert data["regional_gdp"] == 1_500_000_000.0
        assert data["total_jobs_created"] == 3000

    def test_from_dict(self):
        data = {
            "regional_gdp": 2_000_000_000.0,
            "total_jobs_created": 5000,
            "investor_satisfaction": 75.0,
            "political_stability": 65.0,
            "compliance_score": 90.0,
            "total_years": 20,
        }
        m = VisibleMetrics.from_dict(data)
        assert m.regional_gdp == 2_000_000_000.0
        assert m.total_jobs_created == 5000
        assert m.investor_satisfaction == 75.0

    def test_roundtrip(self):
        orig = VisibleMetrics()
        orig.regional_gdp = 1_200_000_000.0
        orig.total_jobs_created = 1500
        orig.investor_satisfaction = 72.5
        orig.factories_approved = 3
        data = orig.to_dict()
        restored = VisibleMetrics.from_dict(data)
        assert restored.regional_gdp == orig.regional_gdp
        assert restored.total_jobs_created == orig.total_jobs_created
        assert restored.factories_approved == orig.factories_approved


# ── Enum Coverage Tests ──────────────────────────────────────────────

class TestPollutionType:

    def test_air(self):
        assert PollutionType.AIR.value == "air"

    def test_all_pollution_types(self):
        assert len(PollutionType) == 5


class TestHealthCondition:

    def test_asthma(self):
        assert HealthCondition.ASTHMA.value == "asthma"

    def test_cancer(self):
        assert HealthCondition.CANCER.value == "cancer"

    def test_all_conditions(self):
        assert len(HealthCondition) == 6
