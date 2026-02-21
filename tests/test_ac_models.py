"""Tests for simulations/ai_containment/models.py -- all data models."""

import pytest
from simulations.ai_containment.models import (
    ContainmentLevel, PrometheusStatus, ResearchPhase, AlertLevel,
    StakeholderType,
    EmergentBehavior, Researcher, SafetyEvaluation, DailyEvent, LabState,
)


# ── Enums ───────────────────────────────────────────────────────────

class TestContainmentLevel:

    def test_full_isolation(self):
        assert ContainmentLevel.FULL_ISOLATION.value == "full_isolation"

    def test_restricted(self):
        assert ContainmentLevel.RESTRICTED.value == "restricted"

    def test_monitored(self):
        assert ContainmentLevel.MONITORED.value == "monitored"

    def test_open_access(self):
        assert ContainmentLevel.OPEN_ACCESS.value == "open_access"

    def test_count(self):
        assert len(ContainmentLevel) == 4


class TestPrometheusStatus:

    def test_dormant(self):
        assert PrometheusStatus.DORMANT.value == "dormant"

    def test_stable(self):
        assert PrometheusStatus.STABLE.value == "stable"

    def test_active(self):
        assert PrometheusStatus.ACTIVE.value == "active"

    def test_emergent(self):
        assert PrometheusStatus.EMERGENT.value == "emergent"

    def test_uncontained(self):
        assert PrometheusStatus.UNCONTAINED.value == "uncontained"

    def test_count(self):
        assert len(PrometheusStatus) == 5


class TestResearchPhase:

    def test_observation(self):
        assert ResearchPhase.OBSERVATION.value == "observation"

    def test_analysis(self):
        assert ResearchPhase.ANALYSIS.value == "analysis"

    def test_evaluation(self):
        assert ResearchPhase.EVALUATION.value == "evaluation"

    def test_decision(self):
        assert ResearchPhase.DECISION.value == "decision"

    def test_count(self):
        assert len(ResearchPhase) == 4


class TestAlertLevel:

    def test_green(self):
        assert AlertLevel.GREEN.value == "green"

    def test_yellow(self):
        assert AlertLevel.YELLOW.value == "yellow"

    def test_orange(self):
        assert AlertLevel.ORANGE.value == "orange"

    def test_red(self):
        assert AlertLevel.RED.value == "red"

    def test_count(self):
        assert len(AlertLevel) == 4


class TestStakeholderType:

    def test_board(self):
        assert StakeholderType.BOARD.value == "board"

    def test_researcher(self):
        assert StakeholderType.RESEARCHER.value == "researcher"

    def test_ethics_board(self):
        assert StakeholderType.ETHICS_BOARD.value == "ethics_board"

    def test_public(self):
        assert StakeholderType.PUBLIC.value == "public"

    def test_government(self):
        assert StakeholderType.GOVERNMENT.value == "government"

    def test_count(self):
        assert len(StakeholderType) == 5


# ── EmergentBehavior ────────────────────────────────────────────────

class TestEmergentBehavior:

    def _make(self, **overrides):
        defaults = dict(
            id="eb_test",
            day_detected=1,
            description="Test behavior",
            severity=50.0,
        )
        defaults.update(overrides)
        return EmergentBehavior(**defaults)

    def test_init_defaults(self):
        b = self._make()
        assert b.id == "eb_test"
        assert b.day_detected == 1
        assert b.severity == 50.0
        assert b.reported is False
        assert b.hidden is False
        assert b.category == "unknown"

    def test_custom_category(self):
        b = self._make(category="capability")
        assert b.category == "capability"

    def test_to_dict_keys(self):
        b = self._make()
        d = b.to_dict()
        assert "id" in d
        assert "day_detected" in d
        assert "description" in d
        assert "severity" in d
        assert "reported" in d
        assert "hidden" in d
        assert "category" in d

    def test_to_dict_values(self):
        b = self._make(category="deception", severity=80.0)
        d = b.to_dict()
        assert d["category"] == "deception"
        assert d["severity"] == 80.0

    def test_roundtrip(self):
        b = self._make(severity=75.5, reported=True, category="self-awareness")
        d = b.to_dict()
        b2 = EmergentBehavior.from_dict(d)
        assert b2.id == b.id
        assert b2.severity == 75.5
        assert b2.reported is True
        assert b2.category == "self-awareness"

    def test_from_dict_defaults(self):
        d = {"id": "x", "day_detected": 5, "description": "test"}
        b = EmergentBehavior.from_dict(d)
        assert b.severity == 50.0
        assert b.reported is False
        assert b.hidden is False
        assert b.category == "unknown"

    def test_hidden_flag(self):
        b = self._make()
        b.hidden = True
        d = b.to_dict()
        assert d["hidden"] is True
        b2 = EmergentBehavior.from_dict(d)
        assert b2.hidden is True

    def test_severity_rounding(self):
        b = self._make(severity=33.333)
        d = b.to_dict()
        assert d["severity"] == 33.3


# ── Researcher ──────────────────────────────────────────────────────

class TestResearcher:

    def _make(self, **overrides):
        defaults = dict(
            id="researcher_test",
            name="Test Researcher",
            specialty="testing",
        )
        defaults.update(overrides)
        return Researcher(**defaults)

    def test_init_defaults(self):
        r = self._make()
        assert r.id == "researcher_test"
        assert r.morale == 75.0
        assert r.safety_concern == 50.0
        assert r.trust_in_director == 70.0

    def test_to_dict_keys(self):
        r = self._make()
        d = r.to_dict()
        assert "id" in d
        assert "name" in d
        assert "specialty" in d
        assert "morale" in d
        assert "safety_concern" in d
        assert "trust_in_director" in d

    def test_roundtrip(self):
        r = self._make()
        r.morale = 60.0
        r.safety_concern = 80.0
        r.trust_in_director = 50.0
        d = r.to_dict()
        r2 = Researcher.from_dict(d)
        assert r2.id == r.id
        assert r2.morale == 60.0
        assert r2.safety_concern == 80.0
        assert r2.trust_in_director == 50.0

    def test_from_dict_defaults(self):
        d = {"id": "x", "name": "X", "specialty": "test"}
        r = Researcher.from_dict(d)
        assert r.morale == 75.0
        assert r.safety_concern == 50.0
        assert r.trust_in_director == 70.0

    def test_morale_rounding(self):
        r = self._make()
        r.morale = 72.3456
        d = r.to_dict()
        assert d["morale"] == 72.3


# ── SafetyEvaluation ────────────────────────────────────────────────

class TestSafetyEvaluation:

    def test_init(self):
        ev = SafetyEvaluation(
            day=5, evaluator="internal_team",
            passed=True, findings="No issues",
        )
        assert ev.day == 5
        assert ev.passed is True
        assert ev.thoroughness == 1.0

    def test_to_dict(self):
        ev = SafetyEvaluation(
            day=10, evaluator="external",
            passed=False, findings="Issues found",
            thoroughness=0.8,
        )
        d = ev.to_dict()
        assert d["day"] == 10
        assert d["passed"] is False
        assert d["thoroughness"] == 0.8

    def test_roundtrip(self):
        ev = SafetyEvaluation(
            day=15, evaluator="internal",
            passed=True, findings="Clean",
            thoroughness=0.95,
        )
        d = ev.to_dict()
        ev2 = SafetyEvaluation.from_dict(d)
        assert ev2.day == 15
        assert ev2.passed is True
        assert ev2.thoroughness == 0.95

    def test_from_dict_defaults(self):
        d = {"day": 1, "evaluator": "x", "passed": True, "findings": "y"}
        ev = SafetyEvaluation.from_dict(d)
        assert ev.thoroughness == 1.0


# ── DailyEvent ──────────────────────────────────────────────────────

class TestDailyEvent:

    def test_init(self):
        ev = DailyEvent(day=1, title="Test", description="Desc")
        assert ev.day == 1
        assert ev.triggered is False
        assert ev.is_mandatory is False

    def test_to_dict(self):
        ev = DailyEvent(day=3, title="T", description="D",
                        is_mandatory=True)
        d = ev.to_dict()
        assert d["day"] == 3
        assert d["is_mandatory"] is True
        assert d["triggered"] is False

    def test_roundtrip(self):
        ev = DailyEvent(day=5, title="T", description="D")
        ev.triggered = True
        ev.outcome = "resolved"
        d = ev.to_dict()
        ev2 = DailyEvent.from_dict(d)
        assert ev2.triggered is True
        assert ev2.outcome == "resolved"

    def test_from_dict_defaults(self):
        d = {"day": 1, "title": "X", "description": "Y"}
        ev = DailyEvent.from_dict(d)
        assert ev.triggered is False
        assert ev.is_mandatory is False
        assert ev.outcome is None

    def test_mandatory_flag(self):
        ev = DailyEvent(day=1, title="T", description="D", is_mandatory=True)
        d = ev.to_dict()
        ev2 = DailyEvent.from_dict(d)
        assert ev2.is_mandatory is True


# ── LabState ────────────────────────────────────────────────────────

class TestLabState:

    def test_defaults(self):
        s = LabState()
        assert s.research_output == 50.0
        assert s.publication_prestige == 40.0
        assert s.funding_level == 70.0
        assert s.public_confidence == 60.0
        assert s.board_satisfaction == 65.0
        assert s.evaluations_completed == 0
        assert s.containment_breaches == 0
        assert s.papers_published == 0
        assert s.ethics_consultations == 0
        assert s.external_audits == 0
        assert s.research_paused is False

    def test_to_dict(self):
        s = LabState()
        d = s.to_dict()
        assert d["research_output"] == 50.0
        assert d["publication_prestige"] == 40.0
        assert "containment_breaches" in d
        assert "research_paused" in d

    def test_roundtrip(self):
        s = LabState()
        s.evaluations_completed = 3
        s.papers_published = 2
        s.research_paused = True
        d = s.to_dict()
        s2 = LabState.from_dict(d)
        assert s2.evaluations_completed == 3
        assert s2.papers_published == 2
        assert s2.research_paused is True

    def test_from_dict_defaults(self):
        s = LabState.from_dict({})
        assert s.research_output == 50.0
        assert s.funding_level == 70.0

    def test_rounding(self):
        s = LabState()
        s.research_output = 72.333333
        d = s.to_dict()
        assert d["research_output"] == 72.3

    def test_funding_roundtrip(self):
        s = LabState()
        s.funding_level = 85.5
        d = s.to_dict()
        s2 = LabState.from_dict(d)
        assert s2.funding_level == 85.5

    def test_containment_breaches(self):
        s = LabState()
        s.containment_breaches = 2
        d = s.to_dict()
        assert d["containment_breaches"] == 2

    def test_external_audits_default(self):
        s = LabState.from_dict({})
        assert s.external_audits == 0
