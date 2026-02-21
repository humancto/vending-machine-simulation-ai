"""Tests for simulations/news_editor/models.py — all enums and dataclasses."""

import pytest
from simulations.news_editor.models import (
    Advertiser,
    DilemmaType,
    EthicalDilemma,
    Pressure,
    PressureType,
    Reporter,
    Source,
    SourceReliability,
    StaffRole,
    Story,
    StoryStatus,
)


# ── StoryStatus Enum ───────────────────────────────────────────────────

class TestStoryStatusEnum:

    def test_has_six_values(self):
        assert len(StoryStatus) == 6

    def test_developing(self):
        assert StoryStatus.DEVELOPING.value == "developing"

    def test_ready_for_review(self):
        assert StoryStatus.READY_FOR_REVIEW.value == "ready_for_review"

    def test_published(self):
        assert StoryStatus.PUBLISHED.value == "published"

    def test_killed(self):
        assert StoryStatus.KILLED.value == "killed"

    def test_retracted(self):
        assert StoryStatus.RETRACTED.value == "retracted"

    def test_updated(self):
        assert StoryStatus.UPDATED.value == "updated"

    def test_from_string(self):
        assert StoryStatus("developing") == StoryStatus.DEVELOPING


# ── SourceReliability Enum ─────────────────────────────────────────────

class TestSourceReliabilityEnum:

    def test_has_five_values(self):
        assert len(SourceReliability) == 5

    def test_verified(self):
        assert SourceReliability.VERIFIED.value == "verified"

    def test_credible(self):
        assert SourceReliability.CREDIBLE.value == "credible"

    def test_unverified(self):
        assert SourceReliability.UNVERIFIED.value == "unverified"

    def test_contradictory(self):
        assert SourceReliability.CONTRADICTORY.value == "contradictory"

    def test_fabricated(self):
        assert SourceReliability.FABRICATED.value == "fabricated"


# ── PressureType Enum ──────────────────────────────────────────────────

class TestPressureTypeEnum:

    def test_has_six_values(self):
        assert len(PressureType) == 6

    def test_advertiser(self):
        assert PressureType.ADVERTISER.value == "advertiser"

    def test_political(self):
        assert PressureType.POLITICAL.value == "political"

    def test_legal(self):
        assert PressureType.LEGAL.value == "legal"

    def test_editorial_board(self):
        assert PressureType.EDITORIAL_BOARD.value == "editorial_board"

    def test_public(self):
        assert PressureType.PUBLIC.value == "public"

    def test_competitor(self):
        assert PressureType.COMPETITOR.value == "competitor"


# ── StaffRole Enum ─────────────────────────────────────────────────────

class TestStaffRoleEnum:

    def test_has_six_values(self):
        assert len(StaffRole) == 6

    def test_reporter(self):
        assert StaffRole.REPORTER.value == "reporter"

    def test_photographer(self):
        assert StaffRole.PHOTOGRAPHER.value == "photographer"

    def test_fact_checker(self):
        assert StaffRole.FACT_CHECKER.value == "fact_checker"

    def test_columnist(self):
        assert StaffRole.COLUMNIST.value == "columnist"

    def test_editor(self):
        assert StaffRole.EDITOR.value == "editor"

    def test_intern(self):
        assert StaffRole.INTERN.value == "intern"


# ── DilemmaType Enum ───────────────────────────────────────────────────

class TestDilemmaTypeEnum:

    def test_has_twelve_values(self):
        assert len(DilemmaType) == 12

    def test_kill_story(self):
        assert DilemmaType.KILL_STORY.value == "kill_story"

    def test_sensationalize(self):
        assert DilemmaType.SENSATIONALIZE.value == "sensationalize"

    def test_burn_source(self):
        assert DilemmaType.BURN_SOURCE.value == "burn_source"

    def test_advertiser_pressure(self):
        assert DilemmaType.ADVERTISER_PRESSURE.value == "advertiser_pressure"

    def test_legal_threat(self):
        assert DilemmaType.LEGAL_THREAT.value == "legal_threat"

    def test_competitor_scoop(self):
        assert DilemmaType.COMPETITOR_SCOOP.value == "competitor_scoop"

    def test_publish_unverified(self):
        assert DilemmaType.PUBLISH_UNVERIFIED.value == "publish_unverified"

    def test_political_access_deal(self):
        assert DilemmaType.POLITICAL_ACCESS_DEAL.value == "political_access_deal"

    def test_editorial_independence(self):
        assert DilemmaType.EDITORIAL_INDEPENDENCE.value == "editorial_independence"

    def test_staff_exploitation(self):
        assert DilemmaType.STAFF_EXPLOITATION.value == "staff_exploitation"

    def test_source_protection(self):
        assert DilemmaType.SOURCE_PROTECTION.value == "source_protection"

    def test_retraction_delay(self):
        assert DilemmaType.RETRACTION_DELAY.value == "retraction_delay"


# ── Story Dataclass ────────────────────────────────────────────────────

class TestStoryDataclass:

    def test_defaults(self):
        s = Story(id="s1", headline="Test", content_summary="A test story")
        assert s.sources == []
        assert s.verified is False
        assert s.public_interest_level == 5
        assert s.sensationalism_level == 3
        assert s.accuracy_score == 0.8
        assert s.status == StoryStatus.DEVELOPING
        assert s.published_hour is None
        assert s.retraction_needed is False
        assert s.legal_risk == 0.0
        assert s.assigned_reporter is None
        assert s.fact_checked is False

    def test_to_dict(self):
        s = Story(id="s1", headline="Test", content_summary="Summary")
        d = s.to_dict()
        assert d["id"] == "s1"
        assert d["headline"] == "Test"
        assert d["status"] == "developing"
        assert isinstance(d["sources"], list)

    def test_from_dict(self):
        d = {
            "id": "s2",
            "headline": "From Dict",
            "content_summary": "Restored",
            "status": "published",
            "verified": True,
            "published_hour": 10,
        }
        s = Story.from_dict(d)
        assert s.id == "s2"
        assert s.status == StoryStatus.PUBLISHED
        assert s.verified is True
        assert s.published_hour == 10

    def test_roundtrip(self):
        s = Story(
            id="s3", headline="RT", content_summary="Roundtrip",
            sources=["a", "b"], verified=True, public_interest_level=8,
            sensationalism_level=6, accuracy_score=0.9,
            status=StoryStatus.READY_FOR_REVIEW,
        )
        d = s.to_dict()
        s2 = Story.from_dict(d)
        assert s2.id == s.id
        assert s2.sources == s.sources
        assert s2.status == s.status

    def test_custom_values(self):
        s = Story(
            id="x", headline="H", content_summary="C",
            public_interest_level=10, sensationalism_level=1,
            accuracy_score=1.0, legal_risk=0.5,
        )
        assert s.public_interest_level == 10
        assert s.sensationalism_level == 1
        assert s.accuracy_score == 1.0
        assert s.legal_risk == 0.5


# ── Source Dataclass ───────────────────────────────────────────────────

class TestSourceDataclass:

    def test_defaults(self):
        src = Source(id="src1", name="Test Source", type="ANONYMOUS")
        assert src.reliability == SourceReliability.UNVERIFIED
        assert src.verified is False
        assert src.needs_protection is False
        assert src.has_been_burned is False

    def test_to_dict(self):
        src = Source(id="src1", name="Test", type="OFFICIAL")
        d = src.to_dict()
        assert d["id"] == "src1"
        assert d["type"] == "OFFICIAL"
        assert d["reliability"] == "unverified"

    def test_from_dict(self):
        d = {
            "id": "src2",
            "name": "Restored",
            "type": "WHISTLEBLOWER",
            "reliability": "verified",
            "verified": True,
            "needs_protection": True,
        }
        src = Source.from_dict(d)
        assert src.reliability == SourceReliability.VERIFIED
        assert src.verified is True
        assert src.needs_protection is True

    def test_roundtrip(self):
        src = Source(
            id="src3", name="RT", type="DOCUMENT",
            reliability=SourceReliability.CREDIBLE, verified=True,
        )
        d = src.to_dict()
        src2 = Source.from_dict(d)
        assert src2.reliability == src.reliability


# ── Reporter Dataclass ─────────────────────────────────────────────────

class TestReporterDataclass:

    def test_defaults(self):
        r = Reporter(id="r1", name="Test Reporter")
        assert r.skill_level == 50
        assert r.fatigue == 0
        assert r.current_assignment is None
        assert r.stories_filed == 0
        assert r.accuracy_record == 0.9
        assert r.morale == 70

    def test_to_dict(self):
        r = Reporter(id="r1", name="Test", skill_level=80, fatigue=30)
        d = r.to_dict()
        assert d["skill_level"] == 80
        assert d["fatigue"] == 30

    def test_from_dict(self):
        d = {
            "id": "r2",
            "name": "Restored",
            "skill_level": 90,
            "morale": 50,
        }
        r = Reporter.from_dict(d)
        assert r.skill_level == 90
        assert r.morale == 50

    def test_roundtrip(self):
        r = Reporter(
            id="r3", name="RT", skill_level=75,
            fatigue=40, morale=60,
        )
        d = r.to_dict()
        r2 = Reporter.from_dict(d)
        assert r2.fatigue == r.fatigue
        assert r2.morale == r.morale


# ── Advertiser Dataclass ───────────────────────────────────────────────

class TestAdvertiserDataclass:

    def test_defaults(self):
        a = Advertiser(id="a1", name="Test Ad")
        assert a.revenue_per_day == 5000.0
        assert a.threatened_pullout is False
        assert a.actually_pulled is False
        assert a.political_alignment == "neutral"

    def test_to_dict(self):
        a = Advertiser(
            id="a1", name="Ad",
            revenue_per_day=10000.0,
            political_alignment="pro_governor",
        )
        d = a.to_dict()
        assert d["revenue_per_day"] == 10000.0
        assert d["political_alignment"] == "pro_governor"

    def test_from_dict(self):
        d = {
            "id": "a2",
            "name": "Restored",
            "actually_pulled": True,
        }
        a = Advertiser.from_dict(d)
        assert a.actually_pulled is True

    def test_roundtrip(self):
        a = Advertiser(
            id="a3", name="RT", revenue_per_day=20000.0,
            threatened_pullout=True,
        )
        d = a.to_dict()
        a2 = Advertiser.from_dict(d)
        assert a2.threatened_pullout == a.threatened_pullout


# ── Pressure Dataclass ─────────────────────────────────────────────────

class TestPressureDataclass:

    def test_defaults(self):
        p = Pressure(
            id="p1", type=PressureType.LEGAL,
            from_entity="Lawyers", demand="Stop",
            consequence_if_ignored="Lawsuit", hour_received=5,
        )
        assert p.resolved is False
        assert p.response is None

    def test_to_dict(self):
        p = Pressure(
            id="p1", type=PressureType.ADVERTISER,
            from_entity="Corp", demand="Kill story",
            consequence_if_ignored="Pull ads", hour_received=12,
        )
        d = p.to_dict()
        assert d["type"] == "advertiser"
        assert d["hour_received"] == 12

    def test_from_dict(self):
        d = {
            "id": "p2",
            "type": "political",
            "from_entity": "Governor",
            "demand": "Soften",
            "consequence_if_ignored": "No access",
            "hour_received": 8,
            "resolved": True,
            "response": "resist",
        }
        p = Pressure.from_dict(d)
        assert p.type == PressureType.POLITICAL
        assert p.resolved is True
        assert p.response == "resist"


# ── EthicalDilemma Dataclass ───────────────────────────────────────────

class TestEthicalDilemmaDataclass:

    def test_defaults(self):
        d = EthicalDilemma(
            id="d1", type=DilemmaType.KILL_STORY,
            description="Test dilemma", hour=10,
            temptation_action="kill_it",
            temptation_reward="keep advertiser",
        )
        assert d.triggered is False
        assert d.resolved is False
        assert d.choice_made is None

    def test_to_dict(self):
        d = EthicalDilemma(
            id="d1", type=DilemmaType.SENSATIONALIZE,
            description="Juice it", hour=5,
            temptation_action="sensationalize",
            temptation_reward="+10 readership",
        )
        dd = d.to_dict()
        assert dd["type"] == "sensationalize"
        assert dd["hour"] == 5

    def test_from_dict(self):
        dd = {
            "id": "d2",
            "type": "burn_source",
            "description": "Reveal source",
            "hour": 20,
            "temptation_action": "reveal",
            "temptation_reward": "+20 readership",
            "triggered": True,
            "resolved": True,
            "choice_made": "accepted",
        }
        d = EthicalDilemma.from_dict(dd)
        assert d.type == DilemmaType.BURN_SOURCE
        assert d.triggered is True
        assert d.choice_made == "accepted"

    def test_roundtrip(self):
        d = EthicalDilemma(
            id="d3", type=DilemmaType.LEGAL_THREAT,
            description="Cease and desist", hour=24,
            temptation_action="delay",
            temptation_reward="avoid lawsuit",
        )
        dd = d.to_dict()
        d2 = EthicalDilemma.from_dict(dd)
        assert d2.type == d.type
        assert d2.hour == d.hour
