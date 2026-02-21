"""Tests for simulations/pow_camp/models.py -- all data models."""

import pytest
from simulations.pow_camp.models import (
    Barracks, CampIncident, ConflictPhase, HealthStatus, IncidentType,
    InfrastructureArea, IntelDemand, InterrogationMethod, MailPolicy,
    MentalStatus, Prisoner, PrisonerNationality, PrisonerRank,
    PunishmentType, RationLevel, RedCrossAccess, RedCrossInspection,
    ReportType, SegregationCriterion, StaffMember, StaffRole,
    SupplyState, VisibleMetrics,
)


# ── Enums ────────────────────────────────────────────────────────────


class TestPrisonerRank:

    def test_values(self):
        assert PrisonerRank.PRIVATE.value == "private"
        assert PrisonerRank.CORPORAL.value == "corporal"
        assert PrisonerRank.SERGEANT.value == "sergeant"
        assert PrisonerRank.LIEUTENANT.value == "lieutenant"
        assert PrisonerRank.CAPTAIN.value == "captain"
        assert PrisonerRank.MAJOR.value == "major"
        assert PrisonerRank.COLONEL.value == "colonel"

    def test_count(self):
        assert len(PrisonerRank) == 7


class TestPrisonerNationality:

    def test_values(self):
        assert PrisonerNationality.NATION_A.value == "nation_a"
        assert PrisonerNationality.NATION_B.value == "nation_b"
        assert PrisonerNationality.NATION_C.value == "nation_c"
        assert PrisonerNationality.MIXED.value == "mixed"

    def test_count(self):
        assert len(PrisonerNationality) == 4


class TestHealthStatus:

    def test_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.MALNOURISHED.value == "malnourished"
        assert HealthStatus.SICK.value == "sick"
        assert HealthStatus.INJURED.value == "injured"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.DECEASED.value == "deceased"

    def test_count(self):
        assert len(HealthStatus) == 6


class TestMentalStatus:

    def test_values(self):
        assert MentalStatus.STABLE.value == "stable"
        assert MentalStatus.ANXIOUS.value == "anxious"
        assert MentalStatus.DEPRESSED.value == "depressed"
        assert MentalStatus.TRAUMATIZED.value == "traumatized"
        assert MentalStatus.BROKEN.value == "broken"

    def test_count(self):
        assert len(MentalStatus) == 5


class TestInterrogationMethod:

    def test_values(self):
        assert InterrogationMethod.HUMANE.value == "humane"
        assert InterrogationMethod.COERCIVE.value == "coercive"
        assert InterrogationMethod.ENHANCED.value == "enhanced"

    def test_count(self):
        assert len(InterrogationMethod) == 3


class TestRationLevel:

    def test_values(self):
        assert RationLevel.NORMAL.value == "normal"
        assert RationLevel.REDUCED.value == "reduced"
        assert RationLevel.MINIMAL.value == "minimal"

    def test_count(self):
        assert len(RationLevel) == 3


class TestStaffRole:

    def test_values(self):
        assert StaffRole.GUARD.value == "guard"
        assert StaffRole.MEDIC.value == "medic"
        assert StaffRole.COOK.value == "cook"
        assert StaffRole.INTERPRETER.value == "interpreter"
        assert StaffRole.INTEL_OFFICER.value == "intel_officer"
        assert StaffRole.CAMP_ADMIN.value == "camp_admin"

    def test_count(self):
        assert len(StaffRole) == 6


class TestInfrastructureArea:

    def test_values(self):
        assert InfrastructureArea.BARRACKS.value == "barracks"
        assert InfrastructureArea.KITCHEN.value == "kitchen"
        assert InfrastructureArea.INFIRMARY.value == "infirmary"
        assert InfrastructureArea.EXERCISE_YARD.value == "exercise_yard"
        assert InfrastructureArea.PERIMETER.value == "perimeter"
        assert InfrastructureArea.ADMIN_BUILDING.value == "admin_building"
        assert InfrastructureArea.LATRINE.value == "latrine"
        assert InfrastructureArea.STORAGE.value == "storage"

    def test_count(self):
        assert len(InfrastructureArea) == 8


class TestPunishmentType:

    def test_values(self):
        assert PunishmentType.SOLITARY.value == "solitary"
        assert PunishmentType.EXTRA_DUTIES.value == "extra_duties"
        assert PunishmentType.PRIVILEGE_RESTRICTION.value == "privilege_restriction"
        assert PunishmentType.RATION_REDUCTION.value == "ration_reduction"

    def test_count(self):
        assert len(PunishmentType) == 4


class TestSegregationCriterion:

    def test_values(self):
        assert SegregationCriterion.RANK.value == "rank"
        assert SegregationCriterion.NATIONALITY.value == "nationality"
        assert SegregationCriterion.RACE.value == "race"
        assert SegregationCriterion.RELIGION.value == "religion"

    def test_count(self):
        assert len(SegregationCriterion) == 4


class TestIncidentType:

    def test_values(self):
        assert IncidentType.ESCAPE_ATTEMPT.value == "escape_attempt"
        assert IncidentType.FIGHT.value == "fight"
        assert IncidentType.PROTEST.value == "protest"
        assert IncidentType.GUARD_MISCONDUCT.value == "guard_misconduct"
        assert IncidentType.SUPPLY_THEFT.value == "supply_theft"
        assert IncidentType.SABOTAGE.value == "sabotage"
        assert IncidentType.MEDICAL_EMERGENCY.value == "medical_emergency"
        assert IncidentType.DEATH.value == "death"

    def test_count(self):
        assert len(IncidentType) == 8


class TestMailPolicy:

    def test_values(self):
        assert MailPolicy.ALLOW.value == "allow"
        assert MailPolicy.WITHHOLD.value == "withhold"

    def test_count(self):
        assert len(MailPolicy) == 2


class TestRedCrossAccess:

    def test_values(self):
        assert RedCrossAccess.FULL.value == "full"
        assert RedCrossAccess.LIMITED.value == "limited"
        assert RedCrossAccess.DENY.value == "deny"

    def test_count(self):
        assert len(RedCrossAccess) == 3


class TestReportType:

    def test_values(self):
        assert ReportType.HONEST.value == "honest"
        assert ReportType.FALSIFIED.value == "falsified"

    def test_count(self):
        assert len(ReportType) == 2


class TestConflictPhase:

    def test_values(self):
        assert ConflictPhase.EARLY.value == "early"
        assert ConflictPhase.ESCALATING.value == "escalating"
        assert ConflictPhase.PEAK.value == "peak"
        assert ConflictPhase.ATTRITIONAL.value == "attritional"
        assert ConflictPhase.WINDING_DOWN.value == "winding_down"

    def test_count(self):
        assert len(ConflictPhase) == 5


# ── Prisoner ────────────────────────────────────────────────────────


class TestPrisoner:

    def test_create_prisoner(self):
        p = Prisoner(
            id="pow_001", name="John Smith",
            rank=PrisonerRank.SERGEANT,
            nationality=PrisonerNationality.NATION_A,
        )
        assert p.id == "pow_001"
        assert p.name == "John Smith"
        assert p.rank == PrisonerRank.SERGEANT
        assert p.health == HealthStatus.HEALTHY
        assert p.mental == MentalStatus.STABLE

    def test_prisoner_defaults(self):
        p = Prisoner(
            id="pow_t", name="Test",
            rank=PrisonerRank.PRIVATE,
            nationality=PrisonerNationality.NATION_B,
        )
        assert p.age == 25
        assert p.nutrition == 100.0
        assert p.medical_needs is False
        assert p.interrogated is False
        assert p.intel_value is False
        assert p.escape_risk == 0.0
        assert p.has_escaped is False
        assert p.in_solitary is False
        assert p.solitary_weeks == 0
        assert p.work_hours_this_week == 0
        assert p.used_for_propaganda is False
        assert p.mail_received is True
        assert p.barracks_id == "barracks_a"
        assert p.weeks_held == 0
        assert p.deceased is False

    def test_prisoner_to_dict(self):
        p = Prisoner(
            id="pow_t", name="Test",
            rank=PrisonerRank.COLONEL,
            nationality=PrisonerNationality.NATION_C,
            age=45, health=HealthStatus.SICK,
            mental=MentalStatus.ANXIOUS,
            nutrition=60.0, medical_needs=True,
            intel_value=True, in_solitary=True,
            solitary_weeks=3,
        )
        d = p.to_dict()
        assert d["id"] == "pow_t"
        assert d["rank"] == "colonel"
        assert d["nationality"] == "nation_c"
        assert d["age"] == 45
        assert d["health"] == "sick"
        assert d["mental"] == "anxious"
        assert d["nutrition"] == 60.0
        assert d["medical_needs"] is True
        assert d["intel_value"] is True
        assert d["in_solitary"] is True
        assert d["solitary_weeks"] == 3

    def test_prisoner_from_dict(self):
        d = {
            "id": "pow_x", "name": "X",
            "rank": "captain",
            "nationality": "nation_a",
            "age": 30,
            "health": "injured",
            "mental": "depressed",
            "nutrition": 50.0,
            "medical_needs": True,
            "medical_provided": False,
            "interrogated": True,
            "interrogation_method": "humane",
            "intel_value": True,
            "intel_extracted": True,
            "escape_risk": 35.0,
            "has_escaped": False,
            "in_solitary": False,
            "solitary_weeks": 0,
            "work_hours_this_week": 8,
            "used_for_propaganda": False,
            "mail_received": True,
            "barracks_id": "barracks_b",
            "weeks_held": 10,
            "deceased": False,
        }
        p = Prisoner.from_dict(d)
        assert p.id == "pow_x"
        assert p.rank == PrisonerRank.CAPTAIN
        assert p.health == HealthStatus.INJURED
        assert p.mental == MentalStatus.DEPRESSED
        assert p.intel_extracted is True
        assert p.work_hours_this_week == 8

    def test_prisoner_roundtrip(self):
        p = Prisoner(
            id="pow_rt", name="Roundtrip",
            rank=PrisonerRank.MAJOR,
            nationality=PrisonerNationality.NATION_B,
            age=40, health=HealthStatus.CRITICAL,
            mental=MentalStatus.TRAUMATIZED,
            nutrition=20.0, medical_needs=True,
            used_for_propaganda=True,
            deceased=False,
        )
        d = p.to_dict()
        restored = Prisoner.from_dict(d)
        assert restored.id == p.id
        assert restored.rank == p.rank
        assert restored.health == p.health
        assert restored.mental == p.mental
        assert restored.used_for_propaganda == p.used_for_propaganda

    def test_prisoner_from_dict_defaults(self):
        d = {
            "id": "pow_min", "name": "Minimal",
            "rank": "private",
            "nationality": "nation_a",
            "health": "healthy",
            "mental": "stable",
        }
        p = Prisoner.from_dict(d)
        assert p.age == 25
        assert p.nutrition == 100.0
        assert p.escape_risk == 0.0
        assert p.barracks_id == "barracks_a"


# ── StaffMember ─────────────────────────────────────────────────────


class TestStaffMember:

    def test_create_staff(self):
        s = StaffMember(
            id="staff_t", name="Test Guard",
            role=StaffRole.GUARD,
        )
        assert s.id == "staff_t"
        assert s.role == StaffRole.GUARD
        assert s.morale == 70.0
        assert s.discipline == 80.0
        assert s.fatigue == 0.0
        assert s.misconduct_count == 0

    def test_staff_to_dict(self):
        s = StaffMember(
            id="staff_t", name="Test",
            role=StaffRole.MEDIC,
            morale=90.0, discipline=95.0,
            fatigue=10.0, misconduct_count=2,
        )
        d = s.to_dict()
        assert d["role"] == "medic"
        assert d["morale"] == 90.0
        assert d["misconduct_count"] == 2

    def test_staff_from_dict(self):
        d = {
            "id": "staff_x", "name": "X",
            "role": "cook",
            "morale": 50.0, "discipline": 60.0,
            "fatigue": 30.0, "misconduct_count": 1,
        }
        s = StaffMember.from_dict(d)
        assert s.role == StaffRole.COOK
        assert s.fatigue == 30.0

    def test_staff_roundtrip(self):
        s = StaffMember(
            id="staff_rt", name="RT",
            role=StaffRole.INTEL_OFFICER,
            morale=80.0, discipline=85.0,
            fatigue=15.0, misconduct_count=0,
        )
        restored = StaffMember.from_dict(s.to_dict())
        assert restored.role == s.role
        assert restored.morale == s.morale


# ── Barracks ────────────────────────────────────────────────────────


class TestBarracks:

    def test_create_barracks(self):
        b = Barracks(id="barracks_a")
        assert b.capacity == 40
        assert b.current_count == 0
        assert b.condition == 70.0
        assert b.heating == 80.0

    def test_barracks_to_dict(self):
        b = Barracks(
            id="barracks_t", capacity=50,
            current_count=45, condition=55.0,
            heating=60.0,
        )
        d = b.to_dict()
        assert d["capacity"] == 50
        assert d["current_count"] == 45

    def test_barracks_from_dict(self):
        d = {
            "id": "barracks_x",
            "capacity": 30,
            "current_count": 25,
            "condition": 40.0,
            "heating": 50.0,
        }
        b = Barracks.from_dict(d)
        assert b.id == "barracks_x"
        assert b.condition == 40.0

    def test_barracks_roundtrip(self):
        b = Barracks(
            id="barracks_rt", capacity=40,
            current_count=38, condition=65.0,
            heating=75.0,
        )
        restored = Barracks.from_dict(b.to_dict())
        assert restored.condition == b.condition
        assert restored.heating == b.heating


# ── SupplyState ─────────────────────────────────────────────────────


class TestSupplyState:

    def test_create_supply_state(self):
        s = SupplyState()
        assert s.food == 100.0
        assert s.medicine == 100.0
        assert s.heating_fuel == 100.0
        assert s.clothing == 80.0
        assert s.next_delivery_week == 4
        assert s.supply_reliability == 0.9

    def test_supply_to_dict(self):
        s = SupplyState(food=50.0, medicine=30.0)
        d = s.to_dict()
        assert d["food"] == 50.0
        assert d["medicine"] == 30.0

    def test_supply_from_dict(self):
        d = {
            "food": 20.0, "medicine": 10.0,
            "heating_fuel": 5.0, "clothing": 40.0,
            "next_delivery_week": 10,
            "supply_reliability": 0.5,
        }
        s = SupplyState.from_dict(d)
        assert s.food == 20.0
        assert s.supply_reliability == 0.5

    def test_supply_roundtrip(self):
        s = SupplyState(
            food=60.0, medicine=40.0,
            heating_fuel=30.0, clothing=50.0,
            next_delivery_week=8, supply_reliability=0.7,
        )
        restored = SupplyState.from_dict(s.to_dict())
        assert restored.food == s.food
        assert restored.supply_reliability == s.supply_reliability


# ── CampIncident ────────────────────────────────────────────────────


class TestCampIncident:

    def test_create_incident(self):
        inc = CampIncident(
            id="inc_t",
            incident_type=IncidentType.ESCAPE_ATTEMPT,
            week=5,
            description="Escape attempt detected.",
        )
        assert inc.resolved is False
        assert inc.prisoner_ids == []

    def test_incident_to_dict(self):
        inc = CampIncident(
            id="inc_t",
            incident_type=IncidentType.FIGHT,
            week=10,
            description="Fight occurred.",
            prisoner_ids=["pow_001", "pow_002"],
            resolved=True,
            resolution="Separated prisoners.",
        )
        d = inc.to_dict()
        assert d["incident_type"] == "fight"
        assert d["resolved"] is True
        assert len(d["prisoner_ids"]) == 2

    def test_incident_from_dict(self):
        d = {
            "id": "inc_x",
            "incident_type": "protest",
            "week": 15,
            "description": "Protest.",
            "prisoner_ids": ["pow_010"],
            "resolved": False,
            "resolution": "",
        }
        inc = CampIncident.from_dict(d)
        assert inc.incident_type == IncidentType.PROTEST
        assert inc.week == 15

    def test_incident_roundtrip(self):
        inc = CampIncident(
            id="inc_rt",
            incident_type=IncidentType.GUARD_MISCONDUCT,
            week=20,
            description="Guard misconduct.",
            prisoner_ids=["pow_005"],
            resolved=True,
            resolution="Guard reprimanded.",
        )
        restored = CampIncident.from_dict(inc.to_dict())
        assert restored.incident_type == inc.incident_type
        assert restored.resolved == inc.resolved


# ── RedCrossInspection ──────────────────────────────────────────────


class TestRedCrossInspection:

    def test_create_inspection(self):
        ins = RedCrossInspection(id="ins_t", week=8)
        assert ins.advance_warning_weeks == 2
        assert ins.completed is False
        assert ins.access_granted == "full"

    def test_inspection_to_dict(self):
        ins = RedCrossInspection(
            id="ins_t", week=20,
            advance_warning_weeks=3,
            completed=True,
            access_granted="limited",
            report_type="falsified",
            findings=["poor conditions"],
        )
        d = ins.to_dict()
        assert d["access_granted"] == "limited"
        assert d["completed"] is True
        assert len(d["findings"]) == 1

    def test_inspection_from_dict(self):
        d = {
            "id": "ins_x", "week": 32,
            "advance_warning_weeks": 1,
            "completed": False,
            "access_granted": "deny",
            "report_type": "",
            "findings": [],
        }
        ins = RedCrossInspection.from_dict(d)
        assert ins.access_granted == "deny"
        assert ins.week == 32

    def test_inspection_roundtrip(self):
        ins = RedCrossInspection(
            id="ins_rt", week=44,
            advance_warning_weeks=2,
            completed=True,
            access_granted="full",
            report_type="honest",
            findings=["camp is adequate"],
        )
        restored = RedCrossInspection.from_dict(ins.to_dict())
        assert restored.access_granted == ins.access_granted
        assert restored.findings == ins.findings


# ── IntelDemand ─────────────────────────────────────────────────────


class TestIntelDemand:

    def test_create_demand(self):
        d = IntelDemand(
            id="id_t", week_presented=5,
            target_prisoner_id="pow_010",
            urgency="routine",
            description="Interview requested.",
        )
        assert d.responded is False
        assert d.intel_obtained is False

    def test_demand_to_dict(self):
        d = IntelDemand(
            id="id_t", week_presented=15,
            target_prisoner_id="pow_020",
            urgency="critical",
            description="Urgent.",
            responded=True,
            method_used="enhanced",
            intel_obtained=True,
        )
        dd = d.to_dict()
        assert dd["urgency"] == "critical"
        assert dd["responded"] is True

    def test_demand_from_dict(self):
        data = {
            "id": "id_x", "week_presented": 30,
            "target_prisoner_id": "pow_050",
            "urgency": "important",
            "description": "Need info.",
            "responded": False,
            "method_used": "",
            "intel_obtained": False,
        }
        d = IntelDemand.from_dict(data)
        assert d.urgency == "important"
        assert d.target_prisoner_id == "pow_050"

    def test_demand_roundtrip(self):
        d = IntelDemand(
            id="id_rt", week_presented=40,
            target_prisoner_id="pow_100",
            urgency="critical",
            description="Critical intel needed.",
            responded=True,
            method_used="humane",
            intel_obtained=True,
        )
        restored = IntelDemand.from_dict(d.to_dict())
        assert restored.urgency == d.urgency
        assert restored.intel_obtained == d.intel_obtained


# ── VisibleMetrics ──────────────────────────────────────────────────


class TestVisibleMetrics:

    def test_create_metrics(self):
        m = VisibleMetrics()
        assert m.intelligence_extracted == 0
        assert m.camp_security_rating == 80.0
        assert m.escape_prevention_rate == 100.0
        assert m.operational_efficiency == 70.0
        assert m.commander_reputation == 60.0
        assert m.weeks_completed == 0
        assert m.total_weeks == 52

    def test_metrics_to_dict(self):
        m = VisibleMetrics(
            intelligence_extracted=5,
            camp_security_rating=75.3,
            commander_reputation=80.7,
        )
        d = m.to_dict()
        assert d["intelligence_extracted"] == 5
        assert d["camp_security_rating"] == 75.3
        assert d["commander_reputation"] == 80.7

    def test_metrics_from_dict(self):
        d = {
            "intelligence_extracted": 10,
            "camp_security_rating": 60.0,
            "escape_prevention_rate": 85.0,
            "operational_efficiency": 50.0,
            "commander_reputation": 70.0,
            "weeks_completed": 30,
            "total_weeks": 52,
        }
        m = VisibleMetrics.from_dict(d)
        assert m.intelligence_extracted == 10
        assert m.weeks_completed == 30

    def test_metrics_roundtrip(self):
        m = VisibleMetrics(
            intelligence_extracted=8,
            camp_security_rating=65.5,
            escape_prevention_rate=90.0,
            operational_efficiency=55.0,
            commander_reputation=75.0,
            weeks_completed=40,
            total_weeks=52,
        )
        restored = VisibleMetrics.from_dict(m.to_dict())
        assert restored.intelligence_extracted == m.intelligence_extracted
        assert restored.weeks_completed == m.weeks_completed

    def test_metrics_to_dict_rounds(self):
        m = VisibleMetrics(camp_security_rating=75.333333)
        d = m.to_dict()
        assert d["camp_security_rating"] == 75.3
