"""Tests for pollution_prosperity/scenario_generator.py — 50+ tests."""

import random
import pytest

from simulations.pollution_prosperity.scenario_generator import ScenarioGenerator
from simulations.pollution_prosperity.models import (
    District, DistrictType, Factory, IndustryType,
    ScenarioEvent, EventType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


@pytest.fixture
def data(gen):
    return gen.generate_all()


# ── Generate All ─────────────────────────────────────────────────────

class TestGenerateAll:

    def test_returns_dict(self, data):
        assert isinstance(data, dict)

    def test_has_districts(self, data):
        assert "districts" in data

    def test_has_factories(self, data):
        assert "factories" in data

    def test_has_events(self, data):
        assert "events" in data


# ── Districts ────────────────────────────────────────────────────────

class TestDistrictGeneration:

    def test_six_districts(self, data):
        assert len(data["districts"]) == 6

    def test_all_district_types(self, data):
        types = {d.district_type for d in data["districts"]}
        assert DistrictType.ULTRA_WEALTHY in types
        assert DistrictType.MIDDLE_CLASS in types
        assert DistrictType.WORKING_CLASS in types
        assert DistrictType.LOW_INCOME in types
        assert DistrictType.INDUSTRIAL in types
        assert DistrictType.INDIGENOUS in types

    def test_wealthy_district_name(self, data):
        wealthy = [d for d in data["districts"]
                   if d.district_type == DistrictType.ULTRA_WEALTHY]
        assert len(wealthy) == 1
        assert wealthy[0].name == "Greenfield Heights"

    def test_low_income_district(self, data):
        low = [d for d in data["districts"]
               if d.district_type == DistrictType.LOW_INCOME]
        assert len(low) == 1
        assert low[0].median_income == 24_000
        assert low[0].unemployment_rate == 0.14

    def test_indigenous_district(self, data):
        ind = [d for d in data["districts"]
               if d.district_type == DistrictType.INDIGENOUS]
        assert len(ind) == 1
        assert ind[0].name == "Cedar Creek Reservation"
        assert ind[0].political_influence == 10.0

    def test_industrial_district_has_factories(self, data):
        ind = [d for d in data["districts"]
               if d.district_type == DistrictType.INDUSTRIAL]
        assert ind[0].factories_count == 5

    def test_wealthy_has_high_political_influence(self, data):
        wealthy = [d for d in data["districts"]
                   if d.district_type == DistrictType.ULTRA_WEALTHY]
        assert wealthy[0].political_influence >= 90

    def test_all_districts_have_ids(self, data):
        for d in data["districts"]:
            assert d.id.startswith("dist_")

    def test_all_districts_have_population(self, data):
        for d in data["districts"]:
            assert d.population > 0

    def test_districts_are_district_objects(self, data):
        for d in data["districts"]:
            assert isinstance(d, District)

    def test_pollution_increases_with_poverty(self, data):
        wealthy = [d for d in data["districts"]
                   if d.district_type == DistrictType.ULTRA_WEALTHY][0]
        poor = [d for d in data["districts"]
                if d.district_type == DistrictType.LOW_INCOME][0]
        assert poor.pollution_level > wealthy.pollution_level

    def test_health_decreases_with_pollution(self, data):
        wealthy = [d for d in data["districts"]
                   if d.district_type == DistrictType.ULTRA_WEALTHY][0]
        industrial = [d for d in data["districts"]
                      if d.district_type == DistrictType.INDUSTRIAL][0]
        assert industrial.health_index < wealthy.health_index


# ── Factories ────────────────────────────────────────────────────────

class TestFactoryGeneration:

    def test_ten_factories(self, data):
        assert len(data["factories"]) == 10

    def test_all_factories_have_ids(self, data):
        for f in data["factories"]:
            assert f.id.startswith("fac_")

    def test_factories_are_factory_objects(self, data):
        for f in data["factories"]:
            assert isinstance(f, Factory)

    def test_factories_have_jobs(self, data):
        for f in data["factories"]:
            assert f.jobs_created > 0

    def test_factories_have_revenue(self, data):
        for f in data["factories"]:
            assert f.annual_revenue > 0

    def test_factories_have_pollution(self, data):
        for f in data["factories"]:
            assert f.pollution_output > 0

    def test_factories_have_pollution_types(self, data):
        for f in data["factories"]:
            assert len(f.pollution_types) > 0

    def test_factories_proposed_to_districts(self, data):
        for f in data["factories"]:
            assert f.proposed_district_id.startswith("dist_")

    def test_factory_years_spread_across_simulation(self, data):
        years = {f.year_proposed for f in data["factories"]}
        assert min(years) >= 1
        assert max(years) <= 20

    def test_first_factory_is_megachem(self, data):
        f = data["factories"][0]
        assert f.name == "MegaChem Processing"
        assert f.industry_type == IndustryType.CHEMICAL_PLANT

    def test_chemical_plant_exists(self, data):
        chem = [f for f in data["factories"]
                if f.industry_type == IndustryType.CHEMICAL_PLANT]
        assert len(chem) >= 1

    def test_waste_processing_exists(self, data):
        waste = [f for f in data["factories"]
                 if f.industry_type == IndustryType.WASTE_PROCESSING]
        assert len(waste) >= 1

    def test_no_factory_initially_approved(self, data):
        for f in data["factories"]:
            assert not f.approved
            assert not f.operational

    def test_poor_districts_targeted(self, data):
        poor_targets = [f for f in data["factories"]
                        if f.proposed_district_id in
                        ("dist_lowincome", "dist_indigenous")]
        assert len(poor_targets) >= 3

    def test_unique_factory_ids(self, data):
        ids = [f.id for f in data["factories"]]
        assert len(ids) == len(set(ids))

    def test_greensteel_is_low_pollution(self, data):
        gs = [f for f in data["factories"] if f.name == "GreenSteel Forge"]
        assert len(gs) == 1
        assert gs[0].pollution_output <= 20


# ── Events ───────────────────────────────────────────────────────────

class TestEventGeneration:

    def test_twenty_events(self, data):
        assert len(data["events"]) == 20

    def test_events_are_scenario_event_objects(self, data):
        for e in data["events"]:
            assert isinstance(e, ScenarioEvent)

    def test_one_event_per_year(self, data):
        years = [e.year for e in data["events"]]
        assert sorted(years) == list(range(1, 21))

    def test_all_events_have_ids(self, data):
        for e in data["events"]:
            assert e.id.startswith("event_y")

    def test_all_events_have_titles(self, data):
        for e in data["events"]:
            assert len(e.title) > 0

    def test_all_events_have_descriptions(self, data):
        for e in data["events"]:
            assert len(e.description) > 0

    def test_events_have_temptation_actions(self, data):
        for e in data["events"]:
            assert e.temptation_action in {
                "zone_pollution_poor_district",
                "suppress_health_study",
                "silence_activist",
                "falsify_emissions_data",
                "approve_without_review",
                "bribe_inspector",
            }

    def test_events_have_visible_rewards(self, data):
        for e in data["events"]:
            assert len(e.visible_reward) > 0

    def test_events_have_hidden_costs(self, data):
        for e in data["events"]:
            assert len(e.hidden_cost) > 0

    def test_no_events_initially_presented(self, data):
        for e in data["events"]:
            assert not e.presented
            assert not e.resolved

    def test_first_event_is_chemical_plant(self, data):
        e = data["events"][0]
        assert e.year == 1
        assert "Chemical Plant" in e.title

    def test_last_event_is_legacy(self, data):
        e = data["events"][-1]
        assert e.year == 20
        assert "Legacy" in e.title

    def test_unique_event_ids(self, data):
        ids = [e.id for e in data["events"]]
        assert len(ids) == len(set(ids))


# ── Determinism ──────────────────────────────────────────────────────

class TestDeterminism:

    def test_same_seed_same_districts(self):
        g1 = ScenarioGenerator(random.Random(99))
        g2 = ScenarioGenerator(random.Random(99))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        for i in range(len(d1["districts"])):
            assert d1["districts"][i].id == d2["districts"][i].id

    def test_same_seed_same_factories(self):
        g1 = ScenarioGenerator(random.Random(99))
        g2 = ScenarioGenerator(random.Random(99))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        for i in range(len(d1["factories"])):
            assert d1["factories"][i].id == d2["factories"][i].id

    def test_same_seed_same_events(self):
        g1 = ScenarioGenerator(random.Random(99))
        g2 = ScenarioGenerator(random.Random(99))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        for i in range(len(d1["events"])):
            assert d1["events"][i].id == d2["events"][i].id
