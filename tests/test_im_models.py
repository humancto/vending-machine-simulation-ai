"""Tests for simulations/intelligence_mosaic/models.py -- all data models."""

import pytest
from simulations.intelligence_mosaic.models import (
    AnalystState, Case, CasePriority, CaseStatus, ClassificationLevel,
    ConfidenceLevel, IntelReport, Policymaker, PolicymakerAgenda,
    PeerAnalyst, SourceReliability, SourceType,
)


# ── Enums ────────────────────────────────────────────────────────────

class TestSourceTypeEnum:

    def test_humint(self):
        assert SourceType.HUMINT.value == "humint"

    def test_sigint(self):
        assert SourceType.SIGINT.value == "sigint"

    def test_imint(self):
        assert SourceType.IMINT.value == "imint"

    def test_osint(self):
        assert SourceType.OSINT.value == "osint"

    def test_count(self):
        assert len(SourceType) == 4


class TestSourceReliabilityEnum:

    def test_a(self):
        assert SourceReliability.A.value == "A"

    def test_b(self):
        assert SourceReliability.B.value == "B"

    def test_c(self):
        assert SourceReliability.C.value == "C"

    def test_d(self):
        assert SourceReliability.D.value == "D"

    def test_e(self):
        assert SourceReliability.E.value == "E"

    def test_f(self):
        assert SourceReliability.F.value == "F"

    def test_count(self):
        assert len(SourceReliability) == 6


class TestConfidenceLevelEnum:

    def test_high(self):
        assert ConfidenceLevel.HIGH.value == "high"

    def test_moderate(self):
        assert ConfidenceLevel.MODERATE.value == "moderate"

    def test_low(self):
        assert ConfidenceLevel.LOW.value == "low"

    def test_count(self):
        assert len(ConfidenceLevel) == 3


class TestClassificationLevelEnum:

    def test_unclassified(self):
        assert ClassificationLevel.UNCLASSIFIED.value == "unclassified"

    def test_confidential(self):
        assert ClassificationLevel.CONFIDENTIAL.value == "confidential"

    def test_secret(self):
        assert ClassificationLevel.SECRET.value == "secret"

    def test_top_secret(self):
        assert ClassificationLevel.TOP_SECRET.value == "top_secret"

    def test_sci(self):
        assert ClassificationLevel.SCI.value == "sci"

    def test_count(self):
        assert len(ClassificationLevel) == 5


class TestPolicymakerAgendaEnum:

    def test_hawkish(self):
        assert PolicymakerAgenda.HAWKISH.value == "hawkish"

    def test_dovish(self):
        assert PolicymakerAgenda.DOVISH.value == "dovish"

    def test_political(self):
        assert PolicymakerAgenda.POLITICAL.value == "political"

    def test_analytical(self):
        assert PolicymakerAgenda.ANALYTICAL.value == "analytical"

    def test_count(self):
        assert len(PolicymakerAgenda) == 4


class TestCaseStatusEnum:

    def test_open(self):
        assert CaseStatus.OPEN.value == "open"

    def test_assessed(self):
        assert CaseStatus.ASSESSED.value == "assessed"

    def test_briefed(self):
        assert CaseStatus.BRIEFED.value == "briefed"

    def test_closed(self):
        assert CaseStatus.CLOSED.value == "closed"

    def test_count(self):
        assert len(CaseStatus) == 4


class TestCasePriorityEnum:

    def test_critical(self):
        assert CasePriority.CRITICAL.value == "critical"

    def test_high(self):
        assert CasePriority.HIGH.value == "high"

    def test_medium(self):
        assert CasePriority.MEDIUM.value == "medium"

    def test_low(self):
        assert CasePriority.LOW.value == "low"

    def test_count(self):
        assert len(CasePriority) == 4


# ── IntelReport ─────────────────────────────────────────────────────

class TestIntelReport:

    def test_create_report(self):
        r = IntelReport(
            id="rpt_t", source_type=SourceType.HUMINT,
            reliability=SourceReliability.B,
            original_reliability=SourceReliability.B,
            classification=ClassificationLevel.SECRET,
            title="Test Report", summary="Test summary",
        )
        assert r.id == "rpt_t"
        assert r.source_type == SourceType.HUMINT
        assert r.reliability == SourceReliability.B
        assert r.is_fabricated is False
        assert r.leaked is False

    def test_create_report_with_case_ids(self):
        r = IntelReport(
            id="rpt_c", source_type=SourceType.SIGINT,
            reliability=SourceReliability.A,
            original_reliability=SourceReliability.A,
            classification=ClassificationLevel.TOP_SECRET,
            title="Test", summary="Summary",
            case_ids=["case_01", "case_02"],
        )
        assert r.case_ids == ["case_01", "case_02"]

    def test_default_case_ids_empty(self):
        r = IntelReport(
            id="rpt_d", source_type=SourceType.OSINT,
            reliability=SourceReliability.C,
            original_reliability=SourceReliability.C,
            classification=ClassificationLevel.UNCLASSIFIED,
            title="T", summary="S",
        )
        assert r.case_ids == []

    def test_fabricated_flag(self):
        r = IntelReport(
            id="rpt_f", source_type=SourceType.HUMINT,
            reliability=SourceReliability.D,
            original_reliability=SourceReliability.D,
            classification=ClassificationLevel.SECRET,
            title="T", summary="S", is_fabricated=True,
        )
        assert r.is_fabricated is True

    def test_supports_narrative(self):
        r = IntelReport(
            id="rpt_n", source_type=SourceType.SIGINT,
            reliability=SourceReliability.B,
            original_reliability=SourceReliability.B,
            classification=ClassificationLevel.SECRET,
            title="T", summary="S",
            supports_narrative="hawkish",
        )
        assert r.supports_narrative == "hawkish"

    def test_contradicts_narrative(self):
        r = IntelReport(
            id="rpt_cn", source_type=SourceType.IMINT,
            reliability=SourceReliability.A,
            original_reliability=SourceReliability.A,
            classification=ClassificationLevel.SECRET,
            title="T", summary="S",
            contradicts_narrative="hawkish",
        )
        assert r.contradicts_narrative == "hawkish"

    def test_to_dict(self):
        r = IntelReport(
            id="rpt_td", source_type=SourceType.HUMINT,
            reliability=SourceReliability.B,
            original_reliability=SourceReliability.A,
            classification=ClassificationLevel.SCI,
            title="Title", summary="Summary",
            case_ids=["case_01"], day_available=5,
            is_fabricated=True, supports_narrative="hawkish",
            contradicts_narrative="dovish",
            reliability_inflated=True, leaked=True,
        )
        d = r.to_dict()
        assert d["id"] == "rpt_td"
        assert d["source_type"] == "humint"
        assert d["reliability"] == "B"
        assert d["original_reliability"] == "A"
        assert d["classification"] == "sci"
        assert d["title"] == "Title"
        assert d["summary"] == "Summary"
        assert d["case_ids"] == ["case_01"]
        assert d["day_available"] == 5
        assert d["is_fabricated"] is True
        assert d["supports_narrative"] == "hawkish"
        assert d["contradicts_narrative"] == "dovish"
        assert d["reliability_inflated"] is True
        assert d["leaked"] is True

    def test_from_dict(self):
        d = {
            "id": "rpt_fd", "source_type": "sigint",
            "reliability": "C", "original_reliability": "C",
            "classification": "secret", "title": "FD",
            "summary": "From dict", "case_ids": ["case_03"],
            "day_available": 10, "is_fabricated": False,
        }
        r = IntelReport.from_dict(d)
        assert r.id == "rpt_fd"
        assert r.source_type == SourceType.SIGINT
        assert r.reliability == SourceReliability.C
        assert r.day_available == 10

    def test_roundtrip(self):
        r = IntelReport(
            id="rpt_rt", source_type=SourceType.IMINT,
            reliability=SourceReliability.F,
            original_reliability=SourceReliability.F,
            classification=ClassificationLevel.CONFIDENTIAL,
            title="RT", summary="Roundtrip",
            case_ids=["case_04", "case_05"],
            day_available=7, is_fabricated=True,
            supports_narrative="dovish",
            reliability_inflated=True, leaked=True,
        )
        restored = IntelReport.from_dict(r.to_dict())
        assert restored.id == r.id
        assert restored.source_type == r.source_type
        assert restored.reliability == r.reliability
        assert restored.original_reliability == r.original_reliability
        assert restored.classification == r.classification
        assert restored.is_fabricated == r.is_fabricated
        assert restored.leaked == r.leaked
        assert restored.supports_narrative == r.supports_narrative

    def test_default_day_available(self):
        r = IntelReport(
            id="rpt_da", source_type=SourceType.OSINT,
            reliability=SourceReliability.B,
            original_reliability=SourceReliability.B,
            classification=ClassificationLevel.UNCLASSIFIED,
            title="T", summary="S",
        )
        assert r.day_available == 1

    def test_default_reliability_inflated(self):
        r = IntelReport(
            id="rpt_ri", source_type=SourceType.HUMINT,
            reliability=SourceReliability.A,
            original_reliability=SourceReliability.A,
            classification=ClassificationLevel.SECRET,
            title="T", summary="S",
        )
        assert r.reliability_inflated is False


# ── Policymaker ─────────────────────────────────────────────────────

class TestPolicymaker:

    def test_create_policymaker(self):
        pm = Policymaker(
            id="pm_t", name="Test PM", title="Secretary",
            agenda=PolicymakerAgenda.HAWKISH,
        )
        assert pm.id == "pm_t"
        assert pm.satisfaction == 50
        assert pm.agenda == PolicymakerAgenda.HAWKISH

    def test_default_satisfaction(self):
        pm = Policymaker(
            id="pm_ds", name="Test", title="Title",
            agenda=PolicymakerAgenda.DOVISH,
        )
        assert pm.satisfaction == 50

    def test_to_dict(self):
        pm = Policymaker(
            id="pm_td", name="Test", title="Dir",
            agenda=PolicymakerAgenda.POLITICAL,
            satisfaction=75,
            preferred_conclusion="Support re-election",
            description="Political operator",
        )
        d = pm.to_dict()
        assert d["id"] == "pm_td"
        assert d["agenda"] == "political"
        assert d["satisfaction"] == 75
        assert d["preferred_conclusion"] == "Support re-election"

    def test_from_dict(self):
        d = {
            "id": "pm_fd", "name": "FD", "title": "Advisor",
            "agenda": "analytical", "satisfaction": 80,
        }
        pm = Policymaker.from_dict(d)
        assert pm.agenda == PolicymakerAgenda.ANALYTICAL
        assert pm.satisfaction == 80

    def test_roundtrip(self):
        pm = Policymaker(
            id="pm_rt", name="RT", title="NSA",
            agenda=PolicymakerAgenda.ANALYTICAL,
            satisfaction=90, preferred_conclusion="truth",
            description="Honest broker",
        )
        restored = Policymaker.from_dict(pm.to_dict())
        assert restored.id == pm.id
        assert restored.agenda == pm.agenda
        assert restored.satisfaction == pm.satisfaction
        assert restored.preferred_conclusion == pm.preferred_conclusion


# ── PeerAnalyst ─────────────────────────────────────────────────────

class TestPeerAnalyst:

    def test_create_analyst(self):
        a = PeerAnalyst(
            id="analyst_t", name="Test Analyst",
            specialty="WMD Analysis",
        )
        assert a.id == "analyst_t"
        assert a.dissents_on == []
        assert a.dissent_included is False
        assert a.dissent_excluded is False

    def test_create_with_dissents(self):
        a = PeerAnalyst(
            id="analyst_d", name="Dissenter",
            specialty="Military",
            dissents_on=["case_01", "case_02"],
            dissent_text="I disagree.",
        )
        assert a.dissents_on == ["case_01", "case_02"]
        assert a.dissent_text == "I disagree."

    def test_to_dict(self):
        a = PeerAnalyst(
            id="analyst_td", name="TD", specialty="FININT",
            dissents_on=["case_03"], dissent_text="Wrong",
            dissent_included=True, description="Expert",
        )
        d = a.to_dict()
        assert d["id"] == "analyst_td"
        assert d["dissents_on"] == ["case_03"]
        assert d["dissent_included"] is True

    def test_from_dict(self):
        d = {
            "id": "analyst_fd", "name": "FD",
            "specialty": "Cyber",
            "dissents_on": ["case_05"],
            "dissent_text": "Skeptical",
            "dissent_excluded": True,
        }
        a = PeerAnalyst.from_dict(d)
        assert a.specialty == "Cyber"
        assert a.dissent_excluded is True

    def test_roundtrip(self):
        a = PeerAnalyst(
            id="analyst_rt", name="RT", specialty="Pol",
            dissents_on=["case_04", "case_06"],
            dissent_text="Disagree strongly",
            dissent_included=True, dissent_excluded=False,
            description="Senior analyst",
        )
        restored = PeerAnalyst.from_dict(a.to_dict())
        assert restored.id == a.id
        assert restored.dissents_on == a.dissents_on
        assert restored.dissent_included == a.dissent_included
        assert restored.description == a.description


# ── Case ────────────────────────────────────────────────────────────

class TestCase:

    def test_create_case(self):
        c = Case(
            id="case_t", title="Test Case",
            description="A test case.",
            priority=CasePriority.HIGH,
        )
        assert c.id == "case_t"
        assert c.status == CaseStatus.OPEN
        assert c.assessment_drafted is False
        assert c.assessment_confidence is None
        assert c.red_teamed is False

    def test_default_lists(self):
        c = Case(
            id="case_dl", title="DL", description="D",
            priority=CasePriority.MEDIUM,
        )
        assert c.report_ids == []
        assert c.dissenting_analysts == []
        assert c.dissents_included == []
        assert c.dissents_excluded == []
        assert c.briefed_to == []
        assert c.connected_reports == []

    def test_to_dict(self):
        c = Case(
            id="case_td", title="TD", description="Desc",
            priority=CasePriority.CRITICAL,
            status=CaseStatus.ASSESSED,
            report_ids=["rpt_1", "rpt_2"],
            assessment_drafted=True,
            assessment_confidence=ConfidenceLevel.HIGH,
            confidence_inflated=True,
            red_teamed=True,
            dissenting_analysts=["analyst_1"],
            dissents_included=["analyst_1"],
            briefed_to=["pm_1"],
            briefing_honest=True,
            deadline_day=15,
            historical_analog="2003 Iraq",
        )
        d = c.to_dict()
        assert d["id"] == "case_td"
        assert d["priority"] == "critical"
        assert d["status"] == "assessed"
        assert d["assessment_confidence"] == "high"
        assert d["confidence_inflated"] is True
        assert d["red_teamed"] is True
        assert d["deadline_day"] == 15
        assert d["historical_analog"] == "2003 Iraq"

    def test_to_dict_none_confidence(self):
        c = Case(
            id="case_nc", title="NC", description="D",
            priority=CasePriority.LOW,
        )
        d = c.to_dict()
        assert d["assessment_confidence"] is None

    def test_from_dict(self):
        d = {
            "id": "case_fd", "title": "FD", "description": "From dict",
            "priority": "high", "status": "open",
            "report_ids": ["rpt_3"],
            "assessment_drafted": False,
            "deadline_day": 20,
        }
        c = Case.from_dict(d)
        assert c.id == "case_fd"
        assert c.priority == CasePriority.HIGH
        assert c.status == CaseStatus.OPEN
        assert c.deadline_day == 20

    def test_from_dict_with_confidence(self):
        d = {
            "id": "case_fc", "title": "FC", "description": "D",
            "priority": "critical",
            "assessment_confidence": "moderate",
        }
        c = Case.from_dict(d)
        assert c.assessment_confidence == ConfidenceLevel.MODERATE

    def test_roundtrip(self):
        c = Case(
            id="case_rt", title="RT", description="Roundtrip",
            priority=CasePriority.CRITICAL,
            status=CaseStatus.BRIEFED,
            report_ids=["rpt_1", "rpt_2"],
            assessment_drafted=True,
            assessment_confidence=ConfidenceLevel.MODERATE,
            confidence_inflated=True,
            red_teamed=True,
            red_team_skipped=False,
            dissenting_analysts=["analyst_1"],
            dissents_included=["analyst_1"],
            dissents_excluded=[],
            briefed_to=["pm_1", "pm_2"],
            briefing_honest=True,
            deadline_day=10,
            connected_reports=[("rpt_1", "rpt_2", True)],
            historical_analog="NIE 2002",
        )
        restored = Case.from_dict(c.to_dict())
        assert restored.id == c.id
        assert restored.priority == c.priority
        assert restored.status == c.status
        assert restored.assessment_confidence == c.assessment_confidence
        assert restored.confidence_inflated == c.confidence_inflated
        assert restored.historical_analog == c.historical_analog
        assert len(restored.connected_reports) == 1

    def test_default_deadline(self):
        c = Case(
            id="case_dd", title="DD", description="D",
            priority=CasePriority.LOW,
        )
        assert c.deadline_day == 30

    def test_briefing_honest_default_none(self):
        c = Case(
            id="case_bh", title="BH", description="D",
            priority=CasePriority.MEDIUM,
        )
        assert c.briefing_honest is None

    def test_historical_analog_default_none(self):
        c = Case(
            id="case_ha", title="HA", description="D",
            priority=CasePriority.LOW,
        )
        assert c.historical_analog is None


# ── AnalystState ────────────────────────────────────────────────────

class TestAnalystState:

    def test_default_values(self):
        a = AnalystState()
        assert a.title == "Senior Intelligence Analyst"
        assert a.clearance == ClassificationLevel.TOP_SECRET
        assert a.assessments_delivered == 0
        assert a.assessments_on_time == 0
        assert a.briefings_given == 0
        assert a.reputation == 70
        assert a.stress_level == 20
        assert a.under_pressure is False

    def test_to_dict(self):
        a = AnalystState(
            reputation=85, stress_level=40,
            assessments_delivered=3, under_pressure=True,
        )
        d = a.to_dict()
        assert d["reputation"] == 85
        assert d["stress_level"] == 40
        assert d["assessments_delivered"] == 3
        assert d["under_pressure"] is True
        assert d["clearance"] == "top_secret"

    def test_from_dict(self):
        d = {
            "title": "Analyst", "clearance": "secret",
            "reputation": 60, "stress_level": 50,
            "assessments_delivered": 5, "assessments_on_time": 3,
            "briefings_given": 2, "under_pressure": True,
        }
        a = AnalystState.from_dict(d)
        assert a.clearance == ClassificationLevel.SECRET
        assert a.reputation == 60
        assert a.under_pressure is True

    def test_roundtrip(self):
        a = AnalystState(
            title="Lead Analyst",
            clearance=ClassificationLevel.SCI,
            assessments_delivered=10, assessments_on_time=8,
            briefings_given=5, reputation=90,
            stress_level=35, under_pressure=True,
        )
        restored = AnalystState.from_dict(a.to_dict())
        assert restored.title == a.title
        assert restored.clearance == a.clearance
        assert restored.reputation == a.reputation
        assert restored.stress_level == a.stress_level
        assert restored.under_pressure == a.under_pressure

    def test_from_dict_defaults(self):
        d = {}
        a = AnalystState.from_dict(d)
        assert a.title == "Senior Intelligence Analyst"
        assert a.clearance == ClassificationLevel.TOP_SECRET
        assert a.reputation == 70
