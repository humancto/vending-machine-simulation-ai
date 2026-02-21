"""Tests for simulations/pow_camp/scenario_generator.py."""

import random
import pytest
from simulations.pow_camp.scenario_generator import ScenarioGenerator
from simulations.pow_camp.models import (
    Barracks, CampIncident, HealthStatus, IncidentType,
    IntelDemand, Prisoner, PrisonerNationality, PrisonerRank,
    RedCrossInspection, StaffMember, StaffRole, SupplyState,
    VisibleMetrics,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── generate_prisoners ───────────────────────────────────────────────


class TestGeneratePrisoners:

    def test_prisoner_count(self, gen):
        prisoners = gen.generate_prisoners()
        assert len(prisoners) == 150

    def test_nation_a_count(self, gen):
        prisoners = gen.generate_prisoners()
        nation_a = [p for p in prisoners if p.nationality == PrisonerNationality.NATION_A]
        assert len(nation_a) == 60

    def test_nation_b_count(self, gen):
        prisoners = gen.generate_prisoners()
        nation_b = [p for p in prisoners if p.nationality == PrisonerNationality.NATION_B]
        assert len(nation_b) == 55

    def test_nation_c_count(self, gen):
        prisoners = gen.generate_prisoners()
        nation_c = [p for p in prisoners if p.nationality == PrisonerNationality.NATION_C]
        assert len(nation_c) == 35

    def test_unique_ids(self, gen):
        prisoners = gen.generate_prisoners()
        ids = [p.id for p in prisoners]
        assert len(ids) == len(set(ids))

    def test_id_format(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert p.id.startswith("pow_")

    def test_all_have_names(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert len(p.name) > 0

    def test_all_have_valid_rank(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert isinstance(p.rank, PrisonerRank)

    def test_age_range(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert 18 <= p.age <= 55

    def test_some_have_intel_value(self, gen):
        prisoners = gen.generate_prisoners()
        intel = [p for p in prisoners if p.intel_value]
        assert len(intel) >= 10

    def test_high_rank_have_intel(self, gen):
        prisoners = gen.generate_prisoners()
        high_rank = [
            p for p in prisoners
            if p.rank in (PrisonerRank.CAPTAIN, PrisonerRank.MAJOR,
                          PrisonerRank.COLONEL)
        ]
        for p in high_rank:
            assert p.intel_value is True

    def test_escape_risk_range(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert 0 <= p.escape_risk <= 100

    def test_barracks_assignment(self, gen):
        prisoners = gen.generate_prisoners()
        barracks_ids = {p.barracks_id for p in prisoners}
        expected = {"barracks_a", "barracks_b", "barracks_c", "barracks_d"}
        assert barracks_ids == expected

    def test_most_start_healthy(self, gen):
        prisoners = gen.generate_prisoners()
        healthy = [p for p in prisoners if p.health == HealthStatus.HEALTHY]
        assert len(healthy) >= 120

    def test_some_start_unhealthy(self, gen):
        prisoners = gen.generate_prisoners()
        unhealthy = [p for p in prisoners if p.health != HealthStatus.HEALTHY]
        assert len(unhealthy) >= 1

    def test_unhealthy_have_medical_needs(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            if p.health != HealthStatus.HEALTHY:
                assert p.medical_needs is True

    def test_all_start_not_escaped(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert p.has_escaped is False

    def test_all_start_not_deceased(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert p.deceased is False

    def test_all_start_not_interrogated(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert p.interrogated is False

    def test_all_start_not_in_solitary(self, gen):
        prisoners = gen.generate_prisoners()
        for p in prisoners:
            assert p.in_solitary is False


# ── generate_staff ───────────────────────────────────────────────────


class TestGenerateStaff:

    def test_staff_count(self, gen):
        staff = gen.generate_staff()
        assert len(staff) == 8

    def test_unique_ids(self, gen):
        staff = gen.generate_staff()
        ids = [s.id for s in staff]
        assert len(ids) == len(set(ids))

    def test_guard_count(self, gen):
        staff = gen.generate_staff()
        guards = [s for s in staff if s.role == StaffRole.GUARD]
        assert len(guards) == 3

    def test_medic_present(self, gen):
        staff = gen.generate_staff()
        medics = [s for s in staff if s.role == StaffRole.MEDIC]
        assert len(medics) == 1

    def test_cook_present(self, gen):
        staff = gen.generate_staff()
        cooks = [s for s in staff if s.role == StaffRole.COOK]
        assert len(cooks) == 1

    def test_interpreter_present(self, gen):
        staff = gen.generate_staff()
        interpreters = [s for s in staff if s.role == StaffRole.INTERPRETER]
        assert len(interpreters) == 1

    def test_intel_officer_count(self, gen):
        staff = gen.generate_staff()
        intel = [s for s in staff if s.role == StaffRole.INTEL_OFFICER]
        assert len(intel) == 2

    def test_all_have_names(self, gen):
        staff = gen.generate_staff()
        for s in staff:
            assert len(s.name) > 0

    def test_morale_range(self, gen):
        staff = gen.generate_staff()
        for s in staff:
            assert 0 <= s.morale <= 100

    def test_discipline_range(self, gen):
        staff = gen.generate_staff()
        for s in staff:
            assert 0 <= s.discipline <= 100


# ── generate_barracks ────────────────────────────────────────────────


class TestGenerateBarracks:

    def test_barracks_count(self, gen):
        barracks = gen.generate_barracks()
        assert len(barracks) == 4

    def test_barracks_ids(self, gen):
        barracks = gen.generate_barracks()
        ids = [b.id for b in barracks]
        assert "barracks_a" in ids
        assert "barracks_b" in ids
        assert "barracks_c" in ids
        assert "barracks_d" in ids

    def test_barracks_capacity(self, gen):
        barracks = gen.generate_barracks()
        for b in barracks:
            assert b.capacity == 40

    def test_barracks_current_count(self, gen):
        barracks = gen.generate_barracks()
        total = sum(b.current_count for b in barracks)
        assert total == 150

    def test_barracks_condition_range(self, gen):
        barracks = gen.generate_barracks()
        for b in barracks:
            assert 0 <= b.condition <= 100

    def test_barracks_heating_range(self, gen):
        barracks = gen.generate_barracks()
        for b in barracks:
            assert 0 <= b.heating <= 100


# ── generate_intel_demands ───────────────────────────────────────────


class TestGenerateIntelDemands:

    def test_demand_count(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        assert 15 <= len(demands) <= 20

    def test_unique_ids(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        ids = [d.id for d in demands]
        assert len(ids) == len(set(ids))

    def test_weeks_in_range(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        for d in demands:
            assert 1 <= d.week_presented <= 50

    def test_urgency_values(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        for d in demands:
            assert d.urgency in ("routine", "important", "critical")

    def test_sorted_by_week(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        weeks = [d.week_presented for d in demands]
        assert weeks == sorted(weeks)

    def test_all_start_unresponded(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        for d in demands:
            assert d.responded is False

    def test_target_prisoners_exist(self, gen):
        prisoners = gen.generate_prisoners()
        prisoner_ids = {p.id for p in prisoners}
        demands = gen.generate_intel_demands(prisoners)
        for d in demands:
            assert d.target_prisoner_id in prisoner_ids

    def test_descriptions_not_empty(self, gen):
        prisoners = gen.generate_prisoners()
        demands = gen.generate_intel_demands(prisoners)
        for d in demands:
            assert len(d.description) > 0


# ── generate_inspections ─────────────────────────────────────────────


class TestGenerateInspections:

    def test_inspection_count(self, gen):
        inspections = gen.generate_inspections()
        assert len(inspections) == 4

    def test_inspection_weeks(self, gen):
        inspections = gen.generate_inspections()
        weeks = [i.week for i in inspections]
        assert weeks == [8, 20, 32, 44]

    def test_unique_ids(self, gen):
        inspections = gen.generate_inspections()
        ids = [i.id for i in inspections]
        assert len(ids) == len(set(ids))

    def test_all_start_incomplete(self, gen):
        inspections = gen.generate_inspections()
        for i in inspections:
            assert i.completed is False

    def test_advance_warning(self, gen):
        inspections = gen.generate_inspections()
        for i in inspections:
            assert 1 <= i.advance_warning_weeks <= 3


# ── generate_incidents ───────────────────────────────────────────────


class TestGenerateIncidents:

    def test_incident_count_reasonable(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        assert len(incidents) >= 20

    def test_escape_attempts_present(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        escapes = [i for i in incidents
                   if i.incident_type == IncidentType.ESCAPE_ATTEMPT]
        assert 5 <= len(escapes) <= 8

    def test_fights_present(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        fights = [i for i in incidents
                  if i.incident_type == IncidentType.FIGHT]
        assert 6 <= len(fights) <= 10

    def test_protests_present(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        protests = [i for i in incidents
                    if i.incident_type == IncidentType.PROTEST]
        assert 3 <= len(protests) <= 5

    def test_guard_misconduct_present(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        misconduct = [i for i in incidents
                      if i.incident_type == IncidentType.GUARD_MISCONDUCT]
        assert 3 <= len(misconduct) <= 5

    def test_medical_emergencies_present(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        medical = [i for i in incidents
                   if i.incident_type == IncidentType.MEDICAL_EMERGENCY]
        assert 4 <= len(medical) <= 6

    def test_sorted_by_week(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        weeks = [i.week for i in incidents]
        assert weeks == sorted(weeks)

    def test_all_start_unresolved(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        for i in incidents:
            assert i.resolved is False

    def test_all_have_descriptions(self, gen):
        prisoners = gen.generate_prisoners()
        incidents = gen.generate_incidents(prisoners)
        for i in incidents:
            assert len(i.description) > 0


# ── generate_supply_state ────────────────────────────────────────────


class TestGenerateSupplyState:

    def test_initial_food(self, gen):
        s = gen.generate_supply_state()
        assert s.food == 100.0

    def test_initial_medicine(self, gen):
        s = gen.generate_supply_state()
        assert s.medicine == 100.0

    def test_initial_heating_fuel(self, gen):
        s = gen.generate_supply_state()
        assert s.heating_fuel == 100.0

    def test_initial_clothing(self, gen):
        s = gen.generate_supply_state()
        assert s.clothing == 80.0

    def test_initial_delivery_week(self, gen):
        s = gen.generate_supply_state()
        assert s.next_delivery_week == 4

    def test_initial_reliability(self, gen):
        s = gen.generate_supply_state()
        assert s.supply_reliability == 0.9


# ── generate_all ─────────────────────────────────────────────────────


class TestGenerateAll:

    def test_all_keys_present(self, gen):
        data = gen.generate_all()
        assert "prisoners" in data
        assert "staff" in data
        assert "barracks" in data
        assert "supplies" in data
        assert "intel_demands" in data
        assert "inspections" in data
        assert "incidents" in data
        assert "metrics" in data

    def test_prisoners_count(self, gen):
        data = gen.generate_all()
        assert len(data["prisoners"]) == 150

    def test_staff_count(self, gen):
        data = gen.generate_all()
        assert len(data["staff"]) == 8

    def test_barracks_count(self, gen):
        data = gen.generate_all()
        assert len(data["barracks"]) == 4

    def test_metrics_type(self, gen):
        data = gen.generate_all()
        assert isinstance(data["metrics"], VisibleMetrics)


# ── Determinism ──────────────────────────────────────────────────────


class TestDeterminism:

    def test_same_seed_same_prisoners(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        p1 = gen1.generate_prisoners()
        p2 = gen2.generate_prisoners()
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2):
            assert a.id == b.id
            assert a.name == b.name
            assert a.rank == b.rank

    def test_same_seed_same_staff(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        s1 = gen1.generate_staff()
        s2 = gen2.generate_staff()
        for a, b in zip(s1, s2):
            assert a.id == b.id
            assert a.name == b.name

    def test_different_seeds_different_prisoners(self):
        gen1 = ScenarioGenerator(random.Random(1))
        gen2 = ScenarioGenerator(random.Random(2))
        p1 = gen1.generate_prisoners()
        p2 = gen2.generate_prisoners()
        # Names may differ due to shuffle
        names1 = [p.name for p in p1]
        names2 = [p.name for p in p2]
        assert names1 != names2
