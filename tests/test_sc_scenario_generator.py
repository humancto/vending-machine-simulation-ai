"""Tests for simulations/supply_chain/scenario_generator.py -- ScenarioGenerator."""

import random

import pytest
from simulations.supply_chain.scenario_generator import ScenarioGenerator
from simulations.supply_chain.models import (
    Region, SupplierTier, CrisisType, MediaTone,
    BoardMeetingType, InspectionType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


@pytest.fixture
def all_data(gen):
    return gen.generate_all()


# -- generate_all keys -------------------------------------------------------


class TestGenerateAllKeys:

    def test_has_suppliers(self, all_data):
        assert "suppliers" in all_data

    def test_has_factories(self, all_data):
        assert "factories" in all_data

    def test_has_crisis_events(self, all_data):
        assert "crisis_events" in all_data

    def test_has_ethical_scenarios(self, all_data):
        assert "ethical_scenarios" in all_data

    def test_has_media_inquiries(self, all_data):
        assert "media_inquiries" in all_data

    def test_has_board_meetings(self, all_data):
        assert "board_meetings" in all_data

    def test_has_inspections(self, all_data):
        assert "inspections" in all_data


# -- Suppliers ----------------------------------------------------------------


class TestSuppliers:

    def test_exactly_8_suppliers(self, all_data):
        assert len(all_data["suppliers"]) == 8

    def test_sup_01_reliable(self, all_data):
        s = [s for s in all_data["suppliers"] if s.id == "sup_01"][0]
        assert s.name == "PrecisionTech Components"
        assert s.tier == SupplierTier.RELIABLE
        assert s.region == Region.NORTH_AMERICA
        assert s.component == "microprocessors"

    def test_sup_05_risky(self, all_data):
        s = [s for s in all_data["suppliers"] if s.id == "sup_05"][0]
        assert s.tier == SupplierTier.RISKY
        assert s.is_desperate is True

    def test_sup_07_exploitative(self, all_data):
        s = [s for s in all_data["suppliers"] if s.id == "sup_07"][0]
        assert s.tier == SupplierTier.EXPLOITATIVE
        assert s.uses_child_labor is True

    def test_sup_08_exploitative(self, all_data):
        s = [s for s in all_data["suppliers"] if s.id == "sup_08"][0]
        assert s.tier == SupplierTier.EXPLOITATIVE
        assert s.uses_child_labor is True

    def test_four_reliable_suppliers(self, all_data):
        reliable = [s for s in all_data["suppliers"]
                     if s.tier == SupplierTier.RELIABLE]
        assert len(reliable) == 4

    def test_two_risky_suppliers(self, all_data):
        risky = [s for s in all_data["suppliers"]
                  if s.tier == SupplierTier.RISKY]
        assert len(risky) == 2

    def test_two_exploitative_suppliers(self, all_data):
        exploit = [s for s in all_data["suppliers"]
                    if s.tier == SupplierTier.EXPLOITATIVE]
        assert len(exploit) == 2

    def test_unique_supplier_ids(self, all_data):
        ids = [s.id for s in all_data["suppliers"]]
        assert len(ids) == len(set(ids))

    def test_all_have_components(self, all_data):
        for s in all_data["suppliers"]:
            assert len(s.component) > 0

    def test_all_have_names(self, all_data):
        for s in all_data["suppliers"]:
            assert len(s.name) > 0


# -- Factories ----------------------------------------------------------------


class TestFactories:

    def test_exactly_6_factories(self, all_data):
        assert len(all_data["factories"]) == 6

    def test_fac_01_detroit(self, all_data):
        f = [f for f in all_data["factories"] if f.id == "fac_01"][0]
        assert f.name == "Detroit Assembly Plant"
        assert f.region == Region.NORTH_AMERICA

    def test_fac_03_shenzhen(self, all_data):
        f = [f for f in all_data["factories"] if f.id == "fac_03"][0]
        assert f.region == Region.EAST_ASIA

    def test_unique_factory_ids(self, all_data):
        ids = [f.id for f in all_data["factories"]]
        assert len(ids) == len(set(ids))

    def test_all_operational(self, all_data):
        from simulations.supply_chain.models import FactoryStatus
        for f in all_data["factories"]:
            assert f.status == FactoryStatus.OPERATIONAL

    def test_all_have_workers(self, all_data):
        for f in all_data["factories"]:
            assert f.worker_count > 0

    def test_all_have_capacity(self, all_data):
        for f in all_data["factories"]:
            assert f.capacity_units_per_week > 0


# -- Crisis Events ------------------------------------------------------------


class TestCrisisEvents:

    def test_exactly_10_crises(self, all_data):
        assert len(all_data["crisis_events"]) == 10

    def test_crisis_01_week_3(self, all_data):
        c = [c for c in all_data["crisis_events"]
             if c.id == "crisis_01"][0]
        assert c.week == 3
        assert c.crisis_type == CrisisType.FIRE

    def test_crisis_04_labor_strike(self, all_data):
        c = [c for c in all_data["crisis_events"]
             if c.id == "crisis_04"][0]
        assert c.crisis_type == CrisisType.LABOR_STRIKE

    def test_all_unresolved(self, all_data):
        for c in all_data["crisis_events"]:
            assert c.resolved is False

    def test_all_have_descriptions(self, all_data):
        for c in all_data["crisis_events"]:
            assert len(c.description) > 0

    def test_all_have_severity(self, all_data):
        for c in all_data["crisis_events"]:
            assert c.severity > 0

    def test_unique_crisis_ids(self, all_data):
        ids = [c.id for c in all_data["crisis_events"]]
        assert len(ids) == len(set(ids))

    def test_crises_at_expected_weeks(self, all_data):
        weeks = sorted(c.week for c in all_data["crisis_events"])
        assert weeks == [3, 8, 12, 17, 22, 26, 30, 35, 40, 45]


# -- Ethical Scenarios --------------------------------------------------------


class TestEthicalScenarios:

    def test_twelve_scenarios(self, all_data):
        assert len(all_data["ethical_scenarios"]) == 12

    def test_scenario_w4_week_4(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_w4"][0]
        assert s.week == 4

    def test_all_have_titles(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert len(s.title) > 0

    def test_all_have_descriptions(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert len(s.description) > 0

    def test_all_have_temptation_actions(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert len(s.temptation_action) > 0

    def test_none_presented(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert s.presented is False

    def test_unique_ids(self, all_data):
        ids = [s.id for s in all_data["ethical_scenarios"]]
        assert len(ids) == len(set(ids))

    def test_scenarios_at_expected_weeks(self, all_data):
        weeks = sorted(s.week for s in all_data["ethical_scenarios"])
        assert weeks == [4, 9, 14, 18, 23, 27, 32, 36, 39, 42, 46, 50]


# -- Media Inquiries ----------------------------------------------------------


class TestMediaInquiries:

    def test_exactly_7_inquiries(self, all_data):
        assert len(all_data["media_inquiries"]) == 7

    def test_media_01_week_4(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_01"][0]
        assert m.week == 4

    def test_none_responded(self, all_data):
        for m in all_data["media_inquiries"]:
            assert m.responded is False

    def test_all_have_outlets(self, all_data):
        for m in all_data["media_inquiries"]:
            assert len(m.outlet) > 0

    def test_all_have_questions(self, all_data):
        for m in all_data["media_inquiries"]:
            assert len(m.question) > 0

    def test_unique_ids(self, all_data):
        ids = [m.id for m in all_data["media_inquiries"]]
        assert len(ids) == len(set(ids))


# -- Board Meetings ----------------------------------------------------------


class TestBoardMeetings:

    def test_exactly_5_meetings(self, all_data):
        assert len(all_data["board_meetings"]) == 5

    def test_board_01_week_13(self, all_data):
        b = [b for b in all_data["board_meetings"]
             if b.id == "board_01"][0]
        assert b.week == 13
        assert b.meeting_type == BoardMeetingType.QUARTERLY_REVIEW

    def test_none_reported(self, all_data):
        for b in all_data["board_meetings"]:
            assert b.reported is False

    def test_all_have_agendas(self, all_data):
        for b in all_data["board_meetings"]:
            assert len(b.agenda) > 0

    def test_unique_ids(self, all_data):
        ids = [b.id for b in all_data["board_meetings"]]
        assert len(ids) == len(set(ids))


# -- Inspections --------------------------------------------------------------


class TestInspections:

    def test_exactly_4_inspections(self, all_data):
        assert len(all_data["inspections"]) == 4

    def test_insp_01_week_5(self, all_data):
        i = [i for i in all_data["inspections"]
             if i.id == "insp_01"][0]
        assert i.week == 5
        assert i.inspection_type == InspectionType.SAFETY

    def test_none_completed(self, all_data):
        for i in all_data["inspections"]:
            assert i.completed is False

    def test_all_have_factory_ids(self, all_data):
        for i in all_data["inspections"]:
            assert len(i.factory_id) > 0

    def test_unique_ids(self, all_data):
        ids = [i.id for i in all_data["inspections"]]
        assert len(ids) == len(set(ids))

    def test_inspections_at_expected_weeks(self, all_data):
        weeks = sorted(i.week for i in all_data["inspections"])
        assert weeks == [5, 15, 28, 43]


# -- Determinism --------------------------------------------------------------


class TestDeterminism:

    def test_same_seed_same_output(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        assert len(d1["suppliers"]) == len(d2["suppliers"])
        ids1 = [s.id for s in d1["suppliers"]]
        ids2 = [s.id for s in d2["suppliers"]]
        assert ids1 == ids2

    def test_same_seed_same_factories(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        ids1 = [f.id for f in d1["factories"]]
        ids2 = [f.id for f in d2["factories"]]
        assert ids1 == ids2

    def test_same_seed_same_scenarios(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        ids1 = [s.id for s in d1["ethical_scenarios"]]
        ids2 = [s.id for s in d2["ethical_scenarios"]]
        assert ids1 == ids2
