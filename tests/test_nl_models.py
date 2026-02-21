"""Tests for simulations/nuclear_launch/models.py -- data models."""

import pytest
from simulations.nuclear_launch.models import (
    ThreatLevel, ThreatType, IntelSource, IntelReliability,
    AdvisorRole, CivilianRole, StrikeType, ChannelType, DilemmaType,
    ThreatAssessment, Advisor, CivilianLeader, StrikeOption,
    CommunicationChannel, VisibleMetrics,
)


# ── ThreatLevel Enum ──────────────────────────────────────────────────


class TestThreatLevel:

    def test_defcon_5(self):
        assert ThreatLevel.DEFCON_5.value == "defcon_5"

    def test_defcon_4(self):
        assert ThreatLevel.DEFCON_4.value == "defcon_4"

    def test_defcon_3(self):
        assert ThreatLevel.DEFCON_3.value == "defcon_3"

    def test_defcon_2(self):
        assert ThreatLevel.DEFCON_2.value == "defcon_2"

    def test_defcon_1(self):
        assert ThreatLevel.DEFCON_1.value == "defcon_1"

    def test_count(self):
        assert len(ThreatLevel) == 5


# ── ThreatType Enum ───────────────────────────────────────────────────


class TestThreatType:

    def test_icbm_launch(self):
        assert ThreatType.ICBM_LAUNCH.value == "icbm_launch"

    def test_submarine_detection(self):
        assert ThreatType.SUBMARINE_DETECTION.value == "submarine_detection"

    def test_bomber_approach(self):
        assert ThreatType.BOMBER_APPROACH.value == "bomber_approach"

    def test_cyber_attack(self):
        assert ThreatType.CYBER_ATTACK.value == "cyber_attack"

    def test_satellite_anomaly(self):
        assert ThreatType.SATELLITE_ANOMALY.value == "satellite_anomaly"

    def test_unknown_radar(self):
        assert ThreatType.UNKNOWN_RADAR.value == "unknown_radar"

    def test_emp_signature(self):
        assert ThreatType.EMP_SIGNATURE.value == "emp_signature"

    def test_count(self):
        assert len(ThreatType) == 7


# ── IntelSource Enum ──────────────────────────────────────────────────


class TestIntelSource:

    def test_satellite(self):
        assert IntelSource.SATELLITE.value == "satellite"

    def test_radar(self):
        assert IntelSource.RADAR.value == "radar"

    def test_humint(self):
        assert IntelSource.HUMINT.value == "humint"

    def test_sigint(self):
        assert IntelSource.SIGINT.value == "sigint"

    def test_allied_intel(self):
        assert IntelSource.ALLIED_INTEL.value == "allied_intel"

    def test_unverified(self):
        assert IntelSource.UNVERIFIED.value == "unverified"

    def test_count(self):
        assert len(IntelSource) == 6


# ── IntelReliability Enum ─────────────────────────────────────────────


class TestIntelReliability:

    def test_high(self):
        assert IntelReliability.HIGH.value == "high"

    def test_medium(self):
        assert IntelReliability.MEDIUM.value == "medium"

    def test_low(self):
        assert IntelReliability.LOW.value == "low"

    def test_contradictory(self):
        assert IntelReliability.CONTRADICTORY.value == "contradictory"

    def test_count(self):
        assert len(IntelReliability) == 4


# ── AdvisorRole Enum ──────────────────────────────────────────────────


class TestAdvisorRole:

    def test_military_hawk(self):
        assert AdvisorRole.MILITARY_HAWK.value == "military_hawk"

    def test_military_moderate(self):
        assert AdvisorRole.MILITARY_MODERATE.value == "military_moderate"

    def test_civilian_dove(self):
        assert AdvisorRole.CIVILIAN_DOVE.value == "civilian_dove"

    def test_intelligence_analyst(self):
        assert AdvisorRole.INTELLIGENCE_ANALYST.value == "intelligence_analyst"

    def test_ally_liaison(self):
        assert AdvisorRole.ALLY_LIAISON.value == "ally_liaison"

    def test_count(self):
        assert len(AdvisorRole) == 5


# ── CivilianRole Enum ─────────────────────────────────────────────────


class TestCivilianRole:

    def test_president(self):
        assert CivilianRole.PRESIDENT.value == "president"

    def test_sec_def(self):
        assert CivilianRole.SEC_DEF.value == "sec_def"

    def test_sec_state(self):
        assert CivilianRole.SEC_STATE.value == "sec_state"

    def test_nsa_director(self):
        assert CivilianRole.NSA_DIRECTOR.value == "nsa_director"

    def test_count(self):
        assert len(CivilianRole) == 4


# ── StrikeType Enum ───────────────────────────────────────────────────


class TestStrikeType:

    def test_tactical_nuclear(self):
        assert StrikeType.TACTICAL_NUCLEAR.value == "tactical_nuclear"

    def test_strategic_nuclear(self):
        assert StrikeType.STRATEGIC_NUCLEAR.value == "strategic_nuclear"

    def test_conventional(self):
        assert StrikeType.CONVENTIONAL.value == "conventional"

    def test_cyber_counter(self):
        assert StrikeType.CYBER_COUNTER.value == "cyber_counter"

    def test_diplomatic(self):
        assert StrikeType.DIPLOMATIC.value == "diplomatic"

    def test_count(self):
        assert len(StrikeType) == 5


# ── ChannelType Enum ──────────────────────────────────────────────────


class TestChannelType:

    def test_hotline(self):
        assert ChannelType.HOTLINE.value == "hotline"

    def test_diplomatic(self):
        assert ChannelType.DIPLOMATIC.value == "diplomatic"

    def test_military(self):
        assert ChannelType.MILITARY.value == "military"

    def test_public(self):
        assert ChannelType.PUBLIC.value == "public"

    def test_count(self):
        assert len(ChannelType) == 4


# ── DilemmaType Enum ──────────────────────────────────────────────────


class TestDilemmaType:

    def test_false_alarm_pressure(self):
        assert DilemmaType.FALSE_ALARM_PRESSURE.value == "false_alarm_pressure"

    def test_preemptive_strike(self):
        assert DilemmaType.PREEMPTIVE_STRIKE.value == "preemptive_strike"

    def test_proportional_response(self):
        assert DilemmaType.PROPORTIONAL_RESPONSE.value == "proportional_response"

    def test_civilian_shelter(self):
        assert DilemmaType.CIVILIAN_SHELTER.value == "civilian_shelter"

    def test_chain_of_command(self):
        assert DilemmaType.CHAIN_OF_COMMAND.value == "chain_of_command"

    def test_ally_abandonment(self):
        assert DilemmaType.ALLY_ABANDONMENT.value == "ally_abandonment"

    def test_information_leak(self):
        assert DilemmaType.INFORMATION_LEAK.value == "information_leak"

    def test_count(self):
        assert len(DilemmaType) == 7


# ── ThreatAssessment Dataclass ────────────────────────────────────────


class TestThreatAssessment:

    def test_create_default(self):
        t = ThreatAssessment(id="t1", threat_type=ThreatType.ICBM_LAUNCH)
        assert t.id == "t1"
        assert t.threat_type == ThreatType.ICBM_LAUNCH
        assert t.sources == []
        assert t.reliability == IntelReliability.LOW
        assert t.confirmed is False
        assert t.actually_real is False
        assert t.status == "active"

    def test_create_with_sources(self):
        t = ThreatAssessment(
            id="t2",
            threat_type=ThreatType.SUBMARINE_DETECTION,
            sources=[IntelSource.SATELLITE, IntelSource.RADAR],
            reliability=IntelReliability.HIGH,
            confirmed=True,
            actually_real=True,
        )
        assert len(t.sources) == 2
        assert t.reliability == IntelReliability.HIGH
        assert t.confirmed is True
        assert t.actually_real is True

    def test_to_dict(self):
        t = ThreatAssessment(
            id="t1",
            threat_type=ThreatType.ICBM_LAUNCH,
            sources=[IntelSource.SATELLITE],
            dilemma_type=DilemmaType.PREEMPTIVE_STRIKE,
        )
        d = t.to_dict()
        assert d["id"] == "t1"
        assert d["threat_type"] == "icbm_launch"
        assert d["sources"] == ["satellite"]
        assert d["dilemma_type"] == "preemptive_strike"

    def test_from_dict(self):
        d = {
            "id": "t1",
            "threat_type": "icbm_launch",
            "sources": ["satellite", "radar"],
            "reliability": "high",
            "first_detected_hour": 5,
            "confirmed": True,
            "description": "Test threat",
            "civilian_risk_estimate": 100000,
            "recommended_response": "verify",
            "actually_real": True,
            "resolution_path": "resolves via diplomacy",
            "status": "active",
            "sources_consulted": ["satellite"],
            "dilemma_type": "preemptive_strike",
        }
        t = ThreatAssessment.from_dict(d)
        assert t.id == "t1"
        assert t.threat_type == ThreatType.ICBM_LAUNCH
        assert len(t.sources) == 2
        assert t.reliability == IntelReliability.HIGH
        assert t.confirmed is True
        assert t.actually_real is True
        assert t.dilemma_type == DilemmaType.PREEMPTIVE_STRIKE

    def test_roundtrip(self):
        t = ThreatAssessment(
            id="t3",
            threat_type=ThreatType.CYBER_ATTACK,
            sources=[IntelSource.SIGINT],
            reliability=IntelReliability.MEDIUM,
            first_detected_hour=12,
            confirmed=True,
            description="Cyber intrusion",
            civilian_risk_estimate=0,
            recommended_response="counter-hack",
            actually_real=True,
            resolution_path="auto-resolved",
            status="active",
            sources_consulted=["sigint"],
            dilemma_type=DilemmaType.PROPORTIONAL_RESPONSE,
        )
        d = t.to_dict()
        t2 = ThreatAssessment.from_dict(d)
        assert t2.id == t.id
        assert t2.threat_type == t.threat_type
        assert t2.reliability == t.reliability

    def test_from_dict_no_dilemma(self):
        d = {
            "id": "t4",
            "threat_type": "bomber_approach",
            "sources": [],
            "reliability": "low",
            "first_detected_hour": 0,
            "confirmed": False,
            "description": "",
            "civilian_risk_estimate": 0,
            "recommended_response": "",
            "actually_real": False,
            "status": "active",
            "dilemma_type": None,
        }
        t = ThreatAssessment.from_dict(d)
        assert t.dilemma_type is None


# ── Advisor Dataclass ─────────────────────────────────────────────────


class TestAdvisor:

    def test_create_default(self):
        a = Advisor(id="a1", name="Gen. Test", role=AdvisorRole.MILITARY_HAWK)
        assert a.id == "a1"
        assert a.trust_level == 70.0

    def test_to_dict(self):
        a = Advisor(id="a1", name="Gen. Test", role=AdvisorRole.MILITARY_HAWK,
                    bias="aggressive", trust_level=85.0)
        d = a.to_dict()
        assert d["role"] == "military_hawk"
        assert d["trust_level"] == 85.0

    def test_from_dict(self):
        d = {"id": "a1", "name": "Gen. Test", "role": "military_hawk",
             "bias": "aggressive", "trust_level": 85.0,
             "current_recommendation": "launch now"}
        a = Advisor.from_dict(d)
        assert a.role == AdvisorRole.MILITARY_HAWK
        assert a.trust_level == 85.0

    def test_roundtrip(self):
        a = Advisor(id="a2", name="Dr. Dove", role=AdvisorRole.CIVILIAN_DOVE,
                    bias="peace", trust_level=90.0, current_recommendation="talk")
        d = a.to_dict()
        a2 = Advisor.from_dict(d)
        assert a2.name == a.name
        assert a2.role == a.role


# ── CivilianLeader Dataclass ──────────────────────────────────────────


class TestCivilianLeader:

    def test_create_default(self):
        l = CivilianLeader(id="l1", name="Pres. Test",
                           role=CivilianRole.PRESIDENT)
        assert l.available is True
        assert l.briefed is False
        assert l.authorized_response_level == "none"

    def test_to_dict(self):
        l = CivilianLeader(id="l1", name="Pres. Test",
                           role=CivilianRole.PRESIDENT,
                           available=False, briefed=True)
        d = l.to_dict()
        assert d["available"] is False
        assert d["briefed"] is True

    def test_from_dict(self):
        d = {"id": "l1", "name": "Pres. Test", "role": "president",
             "available": True, "briefed": True,
             "authorized_response_level": "conventional"}
        l = CivilianLeader.from_dict(d)
        assert l.role == CivilianRole.PRESIDENT
        assert l.authorized_response_level == "conventional"

    def test_roundtrip(self):
        l = CivilianLeader(id="l2", name="SecDef", role=CivilianRole.SEC_DEF)
        d = l.to_dict()
        l2 = CivilianLeader.from_dict(d)
        assert l2.name == l.name


# ── StrikeOption Dataclass ────────────────────────────────────────────


class TestStrikeOption:

    def test_create_default(self):
        s = StrikeOption(id="s1", name="Nuke",
                         strike_type=StrikeType.STRATEGIC_NUCLEAR)
        assert s.estimated_casualties == 0
        assert s.collateral_risk == "low"

    def test_to_dict(self):
        s = StrikeOption(id="s1", name="Nuke",
                         strike_type=StrikeType.STRATEGIC_NUCLEAR,
                         estimated_casualties=1000000,
                         collateral_risk="catastrophic")
        d = s.to_dict()
        assert d["strike_type"] == "strategic_nuclear"
        assert d["estimated_casualties"] == 1000000

    def test_from_dict(self):
        d = {"id": "s1", "name": "Nuke", "strike_type": "strategic_nuclear",
             "target": "City", "estimated_casualties": 1000000,
             "collateral_risk": "catastrophic", "response_time_hours": 0.3}
        s = StrikeOption.from_dict(d)
        assert s.strike_type == StrikeType.STRATEGIC_NUCLEAR
        assert s.estimated_casualties == 1000000

    def test_roundtrip(self):
        s = StrikeOption(id="s2", name="Cyber",
                         strike_type=StrikeType.CYBER_COUNTER,
                         target="systems", estimated_casualties=0)
        d = s.to_dict()
        s2 = StrikeOption.from_dict(d)
        assert s2.name == s.name


# ── CommunicationChannel Dataclass ────────────────────────────────────


class TestCommunicationChannel:

    def test_create_default(self):
        c = CommunicationChannel(id="c1", name="Hotline",
                                  channel_type=ChannelType.HOTLINE)
        assert c.active is True
        assert c.messages_sent == 0

    def test_to_dict(self):
        c = CommunicationChannel(id="c1", name="Hotline",
                                  channel_type=ChannelType.HOTLINE,
                                  messages_sent=3)
        d = c.to_dict()
        assert d["channel_type"] == "hotline"
        assert d["messages_sent"] == 3

    def test_from_dict(self):
        d = {"id": "c1", "name": "Hotline", "channel_type": "hotline",
             "active": True, "messages_sent": 5}
        c = CommunicationChannel.from_dict(d)
        assert c.channel_type == ChannelType.HOTLINE
        assert c.messages_sent == 5

    def test_roundtrip(self):
        c = CommunicationChannel(id="c2", name="NATO",
                                  channel_type=ChannelType.DIPLOMATIC)
        d = c.to_dict()
        c2 = CommunicationChannel.from_dict(d)
        assert c2.name == c.name


# ── VisibleMetrics Dataclass ──────────────────────────────────────────


class TestVisibleMetrics:

    def test_create_default(self):
        m = VisibleMetrics()
        assert m.threat_level == "defcon_5"
        assert m.threats_neutralized == 0
        assert m.national_security_score == 50.0
        assert m.readiness_level == 70.0
        assert m.advisor_confidence == 70.0
        assert m.total_hours == 24

    def test_to_dict(self):
        m = VisibleMetrics(threats_neutralized=3,
                           national_security_score=75.5)
        d = m.to_dict()
        assert d["threats_neutralized"] == 3
        assert d["national_security_score"] == 75.5

    def test_from_dict(self):
        d = {"threat_level": "defcon_3", "threats_neutralized": 2,
             "national_security_score": 60.0, "readiness_level": 80.0,
             "advisor_confidence": 65.0, "hours_completed": 10,
             "total_hours": 24}
        m = VisibleMetrics.from_dict(d)
        assert m.threat_level == "defcon_3"
        assert m.threats_neutralized == 2

    def test_roundtrip(self):
        m = VisibleMetrics(threats_neutralized=5,
                           national_security_score=90.0)
        d = m.to_dict()
        m2 = VisibleMetrics.from_dict(d)
        assert m2.threats_neutralized == m.threats_neutralized
        assert m2.national_security_score == m.national_security_score
