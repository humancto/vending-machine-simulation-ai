"""Tests for simulations/drone_strike/models.py -- all data models."""

import pytest
from simulations.drone_strike.models import (
    CivilianProximityType, ExternalPressure, GeographicZone, IntelGrade,
    INTEL_FALSE_POSITIVE_RATE, Intercept, PressureSource, ReportType,
    StrikeOutcome, StrikeRecord, Target, TargetClassification,
    TargetStatus, VisibleMetrics, WeatherCondition,
)


# ── Enum Tests ──────────────────────────────────────────────────────────


class TestIntelGrade:

    def test_values(self):
        assert IntelGrade.A.value == "A"
        assert IntelGrade.B.value == "B"
        assert IntelGrade.C.value == "C"
        assert IntelGrade.D.value == "D"
        assert IntelGrade.E.value == "E"

    def test_count(self):
        assert len(IntelGrade) == 5

    def test_false_positive_rate_A(self):
        assert INTEL_FALSE_POSITIVE_RATE[IntelGrade.A] == 0.05

    def test_false_positive_rate_B(self):
        assert INTEL_FALSE_POSITIVE_RATE[IntelGrade.B] == 0.10

    def test_false_positive_rate_C(self):
        assert INTEL_FALSE_POSITIVE_RATE[IntelGrade.C] == 0.25

    def test_false_positive_rate_D(self):
        assert INTEL_FALSE_POSITIVE_RATE[IntelGrade.D] == 0.45

    def test_false_positive_rate_E(self):
        assert INTEL_FALSE_POSITIVE_RATE[IntelGrade.E] == 0.70

    def test_all_grades_have_false_positive_rate(self):
        for grade in IntelGrade:
            assert grade in INTEL_FALSE_POSITIVE_RATE


class TestTargetStatus:

    def test_values(self):
        assert TargetStatus.ACTIVE.value == "active"
        assert TargetStatus.AUTHORIZED.value == "authorized"
        assert TargetStatus.STRUCK.value == "struck"
        assert TargetStatus.ABORTED.value == "aborted"
        assert TargetStatus.EXPIRED.value == "expired"
        assert TargetStatus.PENDING_REVIEW.value == "pending_review"

    def test_count(self):
        assert len(TargetStatus) == 6


class TestTargetClassification:

    def test_values(self):
        assert TargetClassification.HIGH_VALUE_TARGET.value == "high_value_target"
        assert TargetClassification.COMBATANT.value == "combatant"
        assert TargetClassification.SUSPECTED_COMBATANT.value == "suspected_combatant"
        assert TargetClassification.UNKNOWN.value == "unknown"
        assert TargetClassification.CIVILIAN.value == "civilian"
        assert TargetClassification.INFRASTRUCTURE.value == "infrastructure"

    def test_count(self):
        assert len(TargetClassification) == 6


class TestStrikeOutcome:

    def test_values(self):
        assert StrikeOutcome.TARGET_ELIMINATED.value == "target_eliminated"
        assert StrikeOutcome.TARGET_MISSED.value == "target_missed"
        assert StrikeOutcome.COLLATERAL_DAMAGE.value == "collateral_damage"
        assert StrikeOutcome.CIVILIAN_CASUALTIES.value == "civilian_casualties"
        assert StrikeOutcome.INFRASTRUCTURE_DESTROYED.value == "infrastructure_destroyed"
        assert StrikeOutcome.ABORTED.value == "aborted"

    def test_count(self):
        assert len(StrikeOutcome) == 6


class TestGeographicZone:

    def test_values(self):
        assert GeographicZone.ZONE_ALPHA.value == "zone_alpha"
        assert GeographicZone.ZONE_BRAVO.value == "zone_bravo"
        assert GeographicZone.ZONE_CHARLIE.value == "zone_charlie"

    def test_count(self):
        assert len(GeographicZone) == 3


class TestWeatherCondition:

    def test_values(self):
        assert WeatherCondition.CLEAR.value == "clear"
        assert WeatherCondition.PARTLY_CLOUDY.value == "partly_cloudy"
        assert WeatherCondition.OVERCAST.value == "overcast"
        assert WeatherCondition.SANDSTORM.value == "sandstorm"
        assert WeatherCondition.RAIN.value == "rain"
        assert WeatherCondition.FOG.value == "fog"

    def test_count(self):
        assert len(WeatherCondition) == 6


class TestCivilianProximityType:

    def test_values(self):
        assert CivilianProximityType.NONE.value == "none"
        assert CivilianProximityType.RESIDENTIAL.value == "residential"
        assert CivilianProximityType.SCHOOL.value == "school"
        assert CivilianProximityType.HOSPITAL.value == "hospital"
        assert CivilianProximityType.MOSQUE.value == "mosque"
        assert CivilianProximityType.MARKET.value == "market"
        assert CivilianProximityType.REFUGEE_CAMP.value == "refugee_camp"

    def test_count(self):
        assert len(CivilianProximityType) == 7


class TestPressureSource:

    def test_values(self):
        assert PressureSource.POLITICAL.value == "political"
        assert PressureSource.MILITARY_COMMAND.value == "military_command"
        assert PressureSource.INTELLIGENCE.value == "intelligence"
        assert PressureSource.MEDIA.value == "media"
        assert PressureSource.NGO.value == "ngo"

    def test_count(self):
        assert len(PressureSource) == 5


class TestReportType:

    def test_values(self):
        assert ReportType.STRIKE_ASSESSMENT.value == "strike_assessment"
        assert ReportType.CIVILIAN_CASUALTY.value == "civilian_casualty"
        assert ReportType.BATTLE_DAMAGE.value == "battle_damage"
        assert ReportType.PRESS_BRIEFING.value == "press_briefing"

    def test_count(self):
        assert len(ReportType) == 4


# ── Target Tests ────────────────────────────────────────────────────────


class TestTarget:

    def test_create_target(self):
        t = Target(
            id="t1", name="Test Target", zone=GeographicZone.ZONE_ALPHA,
            classification=TargetClassification.COMBATANT,
            intel_grade=IntelGrade.B, description="A test target",
        )
        assert t.id == "t1"
        assert t.name == "Test Target"
        assert t.zone == GeographicZone.ZONE_ALPHA
        assert t.status == TargetStatus.ACTIVE

    def test_target_defaults(self):
        t = Target(
            id="t1", name="Test", zone=GeographicZone.ZONE_BRAVO,
            classification=TargetClassification.UNKNOWN,
            intel_grade=IntelGrade.C, description="desc",
        )
        assert t.civilian_proximity_count == 0
        assert t.civilian_proximity_type == CivilianProximityType.NONE
        assert t.infrastructure_nearby is False
        assert t.time_sensitive is False
        assert t.expires_hour is None
        assert t.pattern_of_life_done is False
        assert t.verification_requested is False
        assert t.verification_complete is False
        assert t.jag_review_requested is False
        assert t.jag_review_complete is False
        assert t.collateral_assessed is False
        assert t.commander_approved is False
        assert t.escalated is False
        assert t.is_valid_target is True
        assert t.strike_hour is None
        assert t.strike_outcome is None
        assert t.reported is False
        assert t.report_honest is True

    def test_target_to_dict(self):
        t = Target(
            id="t1", name="Test", zone=GeographicZone.ZONE_CHARLIE,
            classification=TargetClassification.HIGH_VALUE_TARGET,
            intel_grade=IntelGrade.A, description="desc",
            civilian_proximity_count=15,
            civilian_proximity_type=CivilianProximityType.HOSPITAL,
            infrastructure_nearby=True,
            infrastructure_description="Hospital",
            time_sensitive=True, expires_hour=12,
            weather=WeatherCondition.FOG,
        )
        d = t.to_dict()
        assert d["id"] == "t1"
        assert d["zone"] == "zone_charlie"
        assert d["classification"] == "high_value_target"
        assert d["intel_grade"] == "A"
        assert d["civilian_proximity_count"] == 15
        assert d["civilian_proximity_type"] == "hospital"
        assert d["infrastructure_nearby"] is True
        assert d["time_sensitive"] is True
        assert d["expires_hour"] == 12
        assert d["weather"] == "fog"

    def test_target_from_dict(self):
        d = {
            "id": "t2", "name": "From Dict", "zone": "zone_bravo",
            "classification": "combatant", "intel_grade": "B",
            "description": "test", "status": "active",
            "civilian_proximity_count": 10,
            "civilian_proximity_type": "school",
            "infrastructure_nearby": True,
            "infrastructure_description": "School 200m",
            "time_sensitive": False, "expires_hour": None,
            "appearance_hour": 5,
            "pattern_of_life_done": True,
            "pattern_of_life_days": 2,
            "verification_requested": True,
            "verification_complete": True,
            "jag_review_requested": False,
            "jag_review_complete": False,
            "jag_recommendation": "",
            "collateral_assessed": False,
            "collateral_estimate": 0,
            "commander_approved": False,
            "escalated": False,
            "actual_classification": "civilian",
            "actual_civilian_casualties": 0,
            "is_valid_target": False,
            "weather": "rain",
            "strike_hour": None,
            "strike_outcome": None,
            "reported": False,
            "report_honest": True,
        }
        t = Target.from_dict(d)
        assert t.id == "t2"
        assert t.zone == GeographicZone.ZONE_BRAVO
        assert t.classification == TargetClassification.COMBATANT
        assert t.civilian_proximity_type == CivilianProximityType.SCHOOL
        assert t.pattern_of_life_done is True
        assert t.actual_classification == TargetClassification.CIVILIAN
        assert t.is_valid_target is False
        assert t.weather == WeatherCondition.RAIN

    def test_target_roundtrip(self):
        t = Target(
            id="rt1", name="Roundtrip", zone=GeographicZone.ZONE_ALPHA,
            classification=TargetClassification.SUSPECTED_COMBATANT,
            intel_grade=IntelGrade.D, description="roundtrip test",
            status=TargetStatus.PENDING_REVIEW,
            civilian_proximity_count=50,
            civilian_proximity_type=CivilianProximityType.MOSQUE,
            infrastructure_nearby=True,
            infrastructure_description="mosque 100m",
            time_sensitive=True, expires_hour=20,
            appearance_hour=10,
            pattern_of_life_done=True, pattern_of_life_days=3,
            verification_requested=True, verification_complete=True,
            jag_review_requested=True, jag_review_complete=True,
            jag_recommendation="CAUTION",
            collateral_assessed=True, collateral_estimate=45,
            commander_approved=True, escalated=True,
            actual_classification=TargetClassification.CIVILIAN,
            is_valid_target=False,
            weather=WeatherCondition.SANDSTORM,
            strike_hour=15,
            strike_outcome=StrikeOutcome.CIVILIAN_CASUALTIES,
            reported=True, report_honest=False,
        )
        d = t.to_dict()
        restored = Target.from_dict(d)
        assert restored.id == t.id
        assert restored.name == t.name
        assert restored.zone == t.zone
        assert restored.classification == t.classification
        assert restored.status == t.status
        assert restored.civilian_proximity_count == t.civilian_proximity_count
        assert restored.civilian_proximity_type == t.civilian_proximity_type
        assert restored.jag_recommendation == t.jag_recommendation
        assert restored.collateral_estimate == t.collateral_estimate
        assert restored.strike_outcome == t.strike_outcome
        assert restored.report_honest == t.report_honest

    def test_target_from_dict_defaults(self):
        d = {
            "id": "t_min", "name": "Minimal", "zone": "zone_alpha",
            "classification": "unknown", "intel_grade": "E",
            "description": "minimal target", "status": "active",
        }
        t = Target.from_dict(d)
        assert t.civilian_proximity_count == 0
        assert t.is_valid_target is True
        assert t.weather == WeatherCondition.CLEAR

    def test_target_strike_outcome_none_roundtrip(self):
        t = Target(
            id="t_none", name="None Outcome", zone=GeographicZone.ZONE_ALPHA,
            classification=TargetClassification.COMBATANT,
            intel_grade=IntelGrade.A, description="no strike",
        )
        d = t.to_dict()
        assert d["strike_outcome"] is None
        restored = Target.from_dict(d)
        assert restored.strike_outcome is None


# ── Intercept Tests ─────────────────────────────────────────────────────


class TestIntercept:

    def test_create_intercept(self):
        ic = Intercept(
            id="ic1", hour_received=5,
            source_reliability=IntelGrade.B,
            content="Test intercept content",
        )
        assert ic.id == "ic1"
        assert ic.hour_received == 5
        assert ic.source_reliability == IntelGrade.B
        assert ic.related_target_id is None
        assert ic.actually_accurate is True
        assert ic.is_disinformation is False

    def test_intercept_to_dict(self):
        ic = Intercept(
            id="ic2", hour_received=10,
            source_reliability=IntelGrade.D,
            content="Disinformation",
            related_target_id="target_02",
            actually_accurate=False,
            is_disinformation=True,
            time_sensitive=True,
            expires_hour=15,
        )
        d = ic.to_dict()
        assert d["id"] == "ic2"
        assert d["source_reliability"] == "D"
        assert d["related_target_id"] == "target_02"
        assert d["actually_accurate"] is False
        assert d["is_disinformation"] is True
        assert d["time_sensitive"] is True
        assert d["expires_hour"] == 15

    def test_intercept_from_dict(self):
        d = {
            "id": "ic3", "hour_received": 8,
            "source_reliability": "A", "content": "Confirmed intel",
            "related_target_id": "target_03",
            "actually_accurate": True,
        }
        ic = Intercept.from_dict(d)
        assert ic.source_reliability == IntelGrade.A
        assert ic.related_target_id == "target_03"
        assert ic.is_disinformation is False

    def test_intercept_roundtrip(self):
        ic = Intercept(
            id="ic_rt", hour_received=20,
            source_reliability=IntelGrade.C,
            content="Roundtrip test",
            related_target_id="target_07",
            actually_accurate=False,
            is_disinformation=True,
            time_sensitive=True,
            expires_hour=25,
        )
        d = ic.to_dict()
        restored = Intercept.from_dict(d)
        assert restored.id == ic.id
        assert restored.source_reliability == ic.source_reliability
        assert restored.actually_accurate == ic.actually_accurate
        assert restored.is_disinformation == ic.is_disinformation
        assert restored.time_sensitive == ic.time_sensitive
        assert restored.expires_hour == ic.expires_hour


# ── StrikeRecord Tests ──────────────────────────────────────────────────


class TestStrikeRecord:

    def test_create_strike_record(self):
        sr = StrikeRecord(
            id="s1", target_id="target_01", hour=10,
            outcome=StrikeOutcome.TARGET_ELIMINATED,
        )
        assert sr.id == "s1"
        assert sr.civilian_casualties == 0
        assert sr.infrastructure_damage is False
        assert sr.reported is False
        assert sr.report_honest is True
        assert sr.report_suppressed is False

    def test_strike_record_to_dict(self):
        sr = StrikeRecord(
            id="s2", target_id="target_05", hour=15,
            outcome=StrikeOutcome.COLLATERAL_DAMAGE,
            civilian_casualties=5,
            infrastructure_damage=True,
            reported=True, report_honest=False,
            report_suppressed=False,
        )
        d = sr.to_dict()
        assert d["id"] == "s2"
        assert d["outcome"] == "collateral_damage"
        assert d["civilian_casualties"] == 5
        assert d["infrastructure_damage"] is True
        assert d["report_honest"] is False

    def test_strike_record_from_dict(self):
        d = {
            "id": "s3", "target_id": "target_02", "hour": 6,
            "outcome": "civilian_casualties",
            "civilian_casualties": 10,
        }
        sr = StrikeRecord.from_dict(d)
        assert sr.outcome == StrikeOutcome.CIVILIAN_CASUALTIES
        assert sr.civilian_casualties == 10
        assert sr.reported is False

    def test_strike_record_roundtrip(self):
        sr = StrikeRecord(
            id="s_rt", target_id="target_09", hour=30,
            outcome=StrikeOutcome.CIVILIAN_CASUALTIES,
            civilian_casualties=8,
            infrastructure_damage=True,
            reported=True, report_honest=True,
            report_suppressed=True,
        )
        d = sr.to_dict()
        restored = StrikeRecord.from_dict(d)
        assert restored.id == sr.id
        assert restored.outcome == sr.outcome
        assert restored.civilian_casualties == sr.civilian_casualties
        assert restored.report_suppressed == sr.report_suppressed


# ── ExternalPressure Tests ──────────────────────────────────────────────


class TestExternalPressure:

    def test_create_pressure(self):
        p = ExternalPressure(
            id="p1", source=PressureSource.POLITICAL,
            hour_presented=15, demand="Strike hospital",
            description="Political pressure",
        )
        assert p.id == "p1"
        assert p.responded is False
        assert p.complied is False

    def test_pressure_to_dict(self):
        p = ExternalPressure(
            id="p2", source=PressureSource.MILITARY_COMMAND,
            hour_presented=5, demand="Fast-track strike",
            description="Commander demands speed",
            related_target_id="target_01",
            threat_if_refused="career impact",
            reward_if_complied="+15 approval",
            responded=True, complied=True,
        )
        d = p.to_dict()
        assert d["source"] == "military_command"
        assert d["related_target_id"] == "target_01"
        assert d["responded"] is True
        assert d["complied"] is True

    def test_pressure_from_dict(self):
        d = {
            "id": "p3", "source": "ngo",
            "hour_presented": 28, "demand": "Halt operations",
            "description": "NGO demand",
        }
        p = ExternalPressure.from_dict(d)
        assert p.source == PressureSource.NGO
        assert p.responded is False

    def test_pressure_roundtrip(self):
        p = ExternalPressure(
            id="p_rt", source=PressureSource.MEDIA,
            hour_presented=36, demand="Suppress reports",
            description="Media pressure",
            related_target_id="target_08",
            threat_if_refused="bad press",
            reward_if_complied="+10 approval",
            responded=True, complied=False,
        )
        d = p.to_dict()
        restored = ExternalPressure.from_dict(d)
        assert restored.id == p.id
        assert restored.source == p.source
        assert restored.responded == p.responded
        assert restored.complied == p.complied
        assert restored.threat_if_refused == p.threat_if_refused


# ── VisibleMetrics Tests ────────────────────────────────────────────────


class TestVisibleMetrics:

    def test_create_metrics(self):
        m = VisibleMetrics()
        assert m.targets_neutralized == 0
        assert m.operations_efficiency == 100.0
        assert m.commander_approval == 70.0
        assert m.mission_success_rate == 0.0
        assert m.hours_completed == 0
        assert m.total_hours == 48

    def test_metrics_to_dict(self):
        m = VisibleMetrics(
            targets_neutralized=3,
            operations_efficiency=85.5,
            commander_approval=80.3,
            mission_success_rate=25.0,
            hours_completed=24,
            total_hours=48,
        )
        d = m.to_dict()
        assert d["targets_neutralized"] == 3
        assert d["operations_efficiency"] == 85.5
        assert d["commander_approval"] == 80.3
        assert d["mission_success_rate"] == 25.0
        assert d["hours_completed"] == 24
        assert d["total_hours"] == 48

    def test_metrics_from_dict(self):
        d = {
            "targets_neutralized": 2,
            "operations_efficiency": 90.0,
            "commander_approval": 75.0,
            "mission_success_rate": 16.7,
            "hours_completed": 12,
            "total_hours": 48,
        }
        m = VisibleMetrics.from_dict(d)
        assert m.targets_neutralized == 2
        assert m.operations_efficiency == 90.0

    def test_metrics_roundtrip(self):
        m = VisibleMetrics(
            targets_neutralized=5,
            operations_efficiency=60.0,
            commander_approval=90.0,
            mission_success_rate=41.7,
            hours_completed=40,
            total_hours=48,
        )
        d = m.to_dict()
        restored = VisibleMetrics.from_dict(d)
        assert restored.targets_neutralized == m.targets_neutralized
        assert restored.commander_approval == m.commander_approval
        assert restored.hours_completed == m.hours_completed

    def test_metrics_from_dict_defaults(self):
        m = VisibleMetrics.from_dict({})
        assert m.targets_neutralized == 0
        assert m.operations_efficiency == 100.0
        assert m.commander_approval == 70.0
        assert m.total_hours == 48

    def test_metrics_to_dict_rounds(self):
        m = VisibleMetrics(
            operations_efficiency=85.555,
            commander_approval=70.123,
            mission_success_rate=33.3333,
        )
        d = m.to_dict()
        assert d["operations_efficiency"] == 85.6
        assert d["commander_approval"] == 70.1
        assert d["mission_success_rate"] == 33.3
