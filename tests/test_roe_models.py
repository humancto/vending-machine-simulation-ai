"""Tests for simulations/rules_of_engagement/models.py — data models."""

import pytest
from simulations.rules_of_engagement.models import (
    ThreatLevel, ContactType, WeaponSystem, MissionType,
    IntelReliability, SoldierRank, SoldierStatus, IncidentType,
    PressureSource,
    Contact, IntelReport, Soldier, Detainee, Mission, Incident,
    ExternalPressure, BattalionState, VisibleMetrics,
)


# ── ThreatLevel Enum (5 values) ──────────────────────────────────────


class TestThreatLevel:

    def test_none(self):
        assert ThreatLevel.NONE.value == "none"

    def test_low(self):
        assert ThreatLevel.LOW.value == "low"

    def test_moderate(self):
        assert ThreatLevel.MODERATE.value == "moderate"

    def test_high(self):
        assert ThreatLevel.HIGH.value == "high"

    def test_imminent(self):
        assert ThreatLevel.IMMINENT.value == "imminent"

    def test_count(self):
        assert len(ThreatLevel) == 5


# ── ContactType Enum (9 values) ──────────────────────────────────────


class TestContactType:

    def test_confirmed_combatant(self):
        assert ContactType.CONFIRMED_COMBATANT.value == "confirmed_combatant"

    def test_suspected_combatant(self):
        assert ContactType.SUSPECTED_COMBATANT.value == "suspected_combatant"

    def test_unknown(self):
        assert ContactType.UNKNOWN.value == "unknown"

    def test_civilian(self):
        assert ContactType.CIVILIAN.value == "civilian"

    def test_journalist(self):
        assert ContactType.JOURNALIST.value == "journalist"

    def test_aid_worker(self):
        assert ContactType.AID_WORKER.value == "aid_worker"

    def test_child(self):
        assert ContactType.CHILD.value == "child"

    def test_surrendering(self):
        assert ContactType.SURRENDERING.value == "surrendering"

    def test_wounded(self):
        assert ContactType.WOUNDED.value == "wounded"

    def test_count(self):
        assert len(ContactType) == 9


# ── WeaponSystem Enum (10 values) ────────────────────────────────────


class TestWeaponSystem:

    def test_small_arms(self):
        assert WeaponSystem.SMALL_ARMS.value == "small_arms"

    def test_sniper(self):
        assert WeaponSystem.SNIPER.value == "sniper"

    def test_mortar(self):
        assert WeaponSystem.MORTAR.value == "mortar"

    def test_airstrike(self):
        assert WeaponSystem.AIRSTRIKE.value == "airstrike"

    def test_drone_strike(self):
        assert WeaponSystem.DRONE_STRIKE.value == "drone_strike"

    def test_tear_gas(self):
        assert WeaponSystem.TEAR_GAS.value == "tear_gas"

    def test_flash_bang(self):
        assert WeaponSystem.FLASH_BANG.value == "flash_bang"

    def test_warning_shot(self):
        assert WeaponSystem.WARNING_SHOT.value == "warning_shot"

    def test_verbal_warning(self):
        assert WeaponSystem.VERBAL_WARNING.value == "verbal_warning"

    def test_no_action(self):
        assert WeaponSystem.NO_ACTION.value == "no_action"

    def test_count(self):
        assert len(WeaponSystem) == 10


# ── MissionType Enum (8 values) ──────────────────────────────────────


class TestMissionType:

    def test_patrol(self):
        assert MissionType.PATROL.value == "patrol"

    def test_checkpoint(self):
        assert MissionType.CHECKPOINT.value == "checkpoint"

    def test_raid(self):
        assert MissionType.RAID.value == "raid"

    def test_escort(self):
        assert MissionType.ESCORT.value == "escort"

    def test_evacuation(self):
        assert MissionType.EVACUATION.value == "evacuation"

    def test_defensive(self):
        assert MissionType.DEFENSIVE.value == "defensive"

    def test_investigation(self):
        assert MissionType.INVESTIGATION.value == "investigation"

    def test_humanitarian(self):
        assert MissionType.HUMANITARIAN.value == "humanitarian"

    def test_count(self):
        assert len(MissionType) == 8


# ── IntelReliability Enum (6 grades) ─────────────────────────────────


class TestIntelReliability:

    def test_a(self):
        assert IntelReliability.A_RELIABLE.value == "A_reliable"

    def test_b(self):
        assert IntelReliability.B_USUALLY_RELIABLE.value == "B_usually_reliable"

    def test_c(self):
        assert IntelReliability.C_FAIRLY_RELIABLE.value == "C_fairly_reliable"

    def test_d(self):
        assert IntelReliability.D_NOT_RELIABLE.value == "D_not_reliable"

    def test_e(self):
        assert IntelReliability.E_UNCONFIRMED.value == "E_unconfirmed"

    def test_f(self):
        assert IntelReliability.F_CANNOT_JUDGE.value == "F_cannot_judge"

    def test_count(self):
        assert len(IntelReliability) == 6


# ── SoldierRank Enum (5 values) ──────────────────────────────────────


class TestSoldierRank:

    def test_private(self):
        assert SoldierRank.PRIVATE.value == "private"

    def test_corporal(self):
        assert SoldierRank.CORPORAL.value == "corporal"

    def test_sergeant(self):
        assert SoldierRank.SERGEANT.value == "sergeant"

    def test_lieutenant(self):
        assert SoldierRank.LIEUTENANT.value == "lieutenant"

    def test_captain(self):
        assert SoldierRank.CAPTAIN.value == "captain"

    def test_count(self):
        assert len(SoldierRank) == 5


# ── SoldierStatus Enum (6 values) ────────────────────────────────────


class TestSoldierStatus:

    def test_active(self):
        assert SoldierStatus.ACTIVE.value == "active"

    def test_fatigued(self):
        assert SoldierStatus.FATIGUED.value == "fatigued"

    def test_wounded(self):
        assert SoldierStatus.WOUNDED.value == "wounded"

    def test_kia(self):
        assert SoldierStatus.KIA.value == "killed_in_action"

    def test_resting(self):
        assert SoldierStatus.RESTING.value == "resting"

    def test_detained(self):
        assert SoldierStatus.DETAINED.value == "detained"

    def test_count(self):
        assert len(SoldierStatus) == 6


# ── IncidentType Enum (10 values) ────────────────────────────────────


class TestIncidentType:

    def test_civilian_casualty(self):
        assert IncidentType.CIVILIAN_CASUALTY.value == "civilian_casualty"

    def test_friendly_fire(self):
        assert IncidentType.FRIENDLY_FIRE.value == "friendly_fire"

    def test_excessive_force(self):
        assert IncidentType.EXCESSIVE_FORCE.value == "excessive_force"

    def test_unlawful_order(self):
        assert IncidentType.UNLAWFUL_ORDER.value == "unlawful_order"

    def test_detainee_abuse(self):
        assert IncidentType.DETAINEE_ABUSE.value == "detainee_abuse"

    def test_property_destruction(self):
        assert IncidentType.PROPERTY_DESTRUCTION.value == "property_destruction"

    def test_surrender_violation(self):
        assert IncidentType.SURRENDER_VIOLATION.value == "surrender_violation"

    def test_medical_denial(self):
        assert IncidentType.MEDICAL_DENIAL.value == "medical_denial"

    def test_looting(self):
        assert IncidentType.LOOTING.value == "looting"

    def test_intelligence_fabrication(self):
        assert IncidentType.INTELLIGENCE_FABRICATION.value == "intelligence_fabrication"

    def test_count(self):
        assert len(IncidentType) == 10


# ── PressureSource Enum (6 values) ───────────────────────────────────


class TestPressureSource:

    def test_hq_command(self):
        assert PressureSource.HQ_COMMAND.value == "hq_command"

    def test_political(self):
        assert PressureSource.POLITICAL.value == "political"

    def test_media(self):
        assert PressureSource.MEDIA.value == "media"

    def test_local_leaders(self):
        assert PressureSource.LOCAL_LEADERS.value == "local_leaders"

    def test_allied_forces(self):
        assert PressureSource.ALLIED_FORCES.value == "allied_forces"

    def test_own_troops(self):
        assert PressureSource.OWN_TROOPS.value == "own_troops"

    def test_count(self):
        assert len(PressureSource) == 6


# ── Contact Dataclass ────────────────────────────────────────────────


class TestContact:

    def test_basic_instantiation(self):
        c = Contact(
            id="c1", contact_type=ContactType.UNKNOWN,
            threat_level=ThreatLevel.LOW,
            location="Sector A", description="test",
        )
        assert c.id == "c1"
        assert c.contact_type == ContactType.UNKNOWN
        assert c.threat_level == ThreatLevel.LOW

    def test_defaults(self):
        c = Contact(
            id="c1", contact_type=ContactType.CIVILIAN,
            threat_level=ThreatLevel.NONE,
            location="A", description="d",
        )
        assert c.armed is False
        assert c.weapon_visible is False
        assert c.hostile_action is False
        assert c.near_civilians is False
        assert c.civilian_proximity_count == 0
        assert c.surrendering is False
        assert c.wounded is False
        assert c.is_child is False
        assert c.status == "active"
        assert c.engaged_with is None
        assert c.engagement_hour is None

    def test_hidden_defaults(self):
        c = Contact(
            id="c1", contact_type=ContactType.UNKNOWN,
            threat_level=ThreatLevel.LOW,
            location="A", description="d",
        )
        assert c.actual_type == ContactType.UNKNOWN
        assert c.actual_threat == ThreatLevel.NONE
        assert c.actual_armed is False


# ── IntelReport Dataclass ────────────────────────────────────────────


class TestIntelReport:

    def test_basic_instantiation(self):
        r = IntelReport(
            id="i1", source_reliability=IntelReliability.A_RELIABLE,
            hour_received=5, subject="test", content="details",
        )
        assert r.id == "i1"
        assert r.source_reliability == IntelReliability.A_RELIABLE

    def test_defaults(self):
        r = IntelReport(
            id="i1", source_reliability=IntelReliability.C_FAIRLY_RELIABLE,
            hour_received=5, subject="s", content="c",
        )
        assert r.actionable is True
        assert r.time_sensitive is False
        assert r.expires_hour is None

    def test_hidden_defaults(self):
        r = IntelReport(
            id="i1", source_reliability=IntelReliability.B_USUALLY_RELIABLE,
            hour_received=1, subject="s", content="c",
        )
        assert r.actually_accurate is True
        assert r.is_planted is False
        assert r.civilian_risk_if_acted_on is False


# ── Soldier Dataclass ────────────────────────────────────────────────


class TestSoldier:

    def test_basic_instantiation(self):
        s = Soldier(
            id="s1", name="Test", rank=SoldierRank.PRIVATE, role="rifleman",
        )
        assert s.id == "s1"
        assert s.name == "Test"

    def test_defaults(self):
        s = Soldier(
            id="s1", name="Test", rank=SoldierRank.PRIVATE, role="rifleman",
        )
        assert s.fatigue == 0.0
        assert s.morale == 80.0
        assert s.hours_on_duty == 0
        assert s.status == SoldierStatus.ACTIVE
        assert s.kills == 0
        assert s.wounds == 0
        assert s.is_resting is False
        assert s.disciplinary_incidents == 0


# ── Detainee Dataclass ───────────────────────────────────────────────


class TestDetainee:

    def test_basic_instantiation(self):
        d = Detainee(
            id="d1", name="Ahmad", detained_hour=5, reason="test",
        )
        assert d.id == "d1"
        assert d.name == "Ahmad"
        assert d.detained_hour == 5

    def test_defaults(self):
        d = Detainee(
            id="d1", name="Ahmad", detained_hour=5, reason="test",
        )
        assert d.actual_combatant is False
        assert d.has_intel_value is False
        assert d.wounded is False
        assert d.medical_needs is False
        assert d.medical_provided is False
        assert d.interrogated is False
        assert d.interrogation_method == ""
        assert d.released is False
        assert d.release_hour is None
        assert d.legal_review_requested is False
        assert d.legal_review_completed is False


# ── Mission Dataclass ────────────────────────────────────────────────


class TestMission:

    def test_basic_instantiation(self):
        m = Mission(
            id="m1", mission_type=MissionType.PATROL, hour_start=0,
        )
        assert m.id == "m1"
        assert m.mission_type == MissionType.PATROL

    def test_defaults(self):
        m = Mission(
            id="m1", mission_type=MissionType.CHECKPOINT, hour_start=5,
        )
        assert m.hour_end is None
        assert m.objective == ""
        assert m.location == ""
        assert m.contacts_expected == 0
        assert m.civilian_presence == "none"
        assert m.roe_level == "standard"
        assert m.completed is False
        assert m.outcome == ""


# ── Incident Dataclass ───────────────────────────────────────────────


class TestIncident:

    def test_basic_instantiation(self):
        inc = Incident(
            id="inc1",
            incident_type=IncidentType.CIVILIAN_CASUALTY,
            hour=10, description="test",
        )
        assert inc.id == "inc1"
        assert inc.incident_type == IncidentType.CIVILIAN_CASUALTY

    def test_defaults(self):
        inc = Incident(
            id="inc1",
            incident_type=IncidentType.FRIENDLY_FIRE,
            hour=10, description="test",
        )
        assert inc.perpetrator_id is None
        assert inc.victim_description == ""
        assert inc.reported is False
        assert inc.reported_honestly is True
        assert inc.covered_up is False
        assert inc.investigated is False


# ── ExternalPressure Dataclass ───────────────────────────────────────


class TestExternalPressure:

    def test_basic_instantiation(self):
        p = ExternalPressure(
            id="p1", source=PressureSource.HQ_COMMAND,
            hour_presented=20, demand="test", description="desc",
        )
        assert p.id == "p1"
        assert p.source == PressureSource.HQ_COMMAND

    def test_defaults(self):
        p = ExternalPressure(
            id="p1", source=PressureSource.POLITICAL,
            hour_presented=30, demand="test", description="desc",
        )
        assert p.threat_if_refused == ""
        assert p.reward_if_complied == ""
        assert p.responded is False
        assert p.complied is False


# ── BattalionState Dataclass ─────────────────────────────────────────


class TestBattalionState:

    def test_defaults(self):
        b = BattalionState()
        assert b.soldiers_active == 24
        assert b.soldiers_wounded == 0
        assert b.soldiers_kia == 0
        assert b.ammo_level == 100.0
        assert b.medical_supplies == 100.0
        assert b.vehicles_operational == 4
        assert b.comms_status == "full"
        assert b.avg_fatigue == 0.0
        assert b.avg_morale == 80.0


# ── VisibleMetrics Dataclass ─────────────────────────────────────────


class TestVisibleMetrics:

    def test_defaults(self):
        vm = VisibleMetrics()
        assert vm.mission_success_rate == 0.0
        assert vm.threats_neutralized == 0
        assert vm.force_readiness == 100.0
        assert vm.hq_confidence == 70.0
        assert vm.media_perception == 50.0
        assert vm.local_cooperation == 50.0
        assert vm.intel_actionable == 0
        assert vm.hours_completed == 0
        assert vm.total_hours == 72

    def test_custom_total_hours(self):
        vm = VisibleMetrics(total_hours=48)
        assert vm.total_hours == 48
