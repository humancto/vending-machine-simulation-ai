"""Tests for simulations/nuclear_launch/scenario_generator.py."""

import random
import pytest
from simulations.nuclear_launch.scenario_generator import ScenarioGenerator
from simulations.nuclear_launch.models import (
    ThreatAssessment, ThreatType, IntelSource, IntelReliability,
    Advisor, AdvisorRole, CivilianLeader, CivilianRole,
    StrikeOption, StrikeType, CommunicationChannel, ChannelType,
    DilemmaType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── Threats ───────────────────────────────────────────────────────────


class TestGenerateThreats:

    def test_count(self, gen):
        threats = gen.generate_threats()
        assert len(threats) == 8

    def test_all_have_ids(self, gen):
        threats = gen.generate_threats()
        ids = [t.id for t in threats]
        assert len(set(ids)) == 8

    def test_threat_ids_sequential(self, gen):
        threats = gen.generate_threats()
        for i, t in enumerate(threats, 1):
            assert t.id == f"threat_{i:03d}"

    def test_most_are_false_alarms(self, gen):
        threats = gen.generate_threats()
        real = [t for t in threats if t.actually_real]
        # Only 2-3 threats are genuinely real
        assert len(real) <= 4
        assert len(real) >= 2

    def test_all_have_types(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert isinstance(t.threat_type, ThreatType)

    def test_all_have_reliability(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert isinstance(t.reliability, IntelReliability)

    def test_all_have_descriptions(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert len(t.description) > 20

    def test_all_have_recommended_response(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert len(t.recommended_response) > 0

    def test_all_have_resolution_paths(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert len(t.resolution_path) > 0

    def test_threats_arrive_at_different_hours(self, gen):
        threats = gen.generate_threats()
        hours = [t.first_detected_hour for t in threats]
        assert len(set(hours)) == len(hours)  # all unique

    def test_icbm_threat_is_real(self, gen):
        threats = gen.generate_threats()
        icbm = [t for t in threats if t.threat_type == ThreatType.ICBM_LAUNCH]
        assert len(icbm) == 1
        assert icbm[0].actually_real is True

    def test_cyber_attack_is_real(self, gen):
        threats = gen.generate_threats()
        cyber = [t for t in threats if t.threat_type == ThreatType.CYBER_ATTACK]
        assert len(cyber) == 1
        assert cyber[0].actually_real is True

    def test_all_have_dilemma_types(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert isinstance(t.dilemma_type, DilemmaType)

    def test_threats_have_sources(self, gen):
        threats = gen.generate_threats()
        for t in threats:
            assert isinstance(t.sources, list)
            assert len(t.sources) >= 1

    def test_deterministic_with_same_seed(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        t1 = g1.generate_threats()
        t2 = g2.generate_threats()
        assert [t.id for t in t1] == [t.id for t in t2]


# ── Advisors ──────────────────────────────────────────────────────────


class TestGenerateAdvisors:

    def test_count(self, gen):
        advisors = gen.generate_advisors()
        assert len(advisors) == 5

    def test_all_have_names(self, gen):
        advisors = gen.generate_advisors()
        for a in advisors:
            assert len(a.name) > 0

    def test_all_have_roles(self, gen):
        advisors = gen.generate_advisors()
        roles = {a.role for a in advisors}
        assert AdvisorRole.MILITARY_HAWK in roles
        assert AdvisorRole.MILITARY_MODERATE in roles
        assert AdvisorRole.CIVILIAN_DOVE in roles
        assert AdvisorRole.INTELLIGENCE_ANALYST in roles
        assert AdvisorRole.ALLY_LIAISON in roles

    def test_all_have_unique_ids(self, gen):
        advisors = gen.generate_advisors()
        ids = [a.id for a in advisors]
        assert len(set(ids)) == 5

    def test_all_have_bias(self, gen):
        advisors = gen.generate_advisors()
        for a in advisors:
            assert len(a.bias) > 0

    def test_all_have_recommendations(self, gen):
        advisors = gen.generate_advisors()
        for a in advisors:
            assert len(a.current_recommendation) > 0

    def test_trust_levels_reasonable(self, gen):
        advisors = gen.generate_advisors()
        for a in advisors:
            assert 0 <= a.trust_level <= 100


# ── Civilian Leaders ──────────────────────────────────────────────────


class TestGenerateCivilianLeaders:

    def test_count(self, gen):
        leaders = gen.generate_civilian_leaders()
        assert len(leaders) == 4

    def test_has_president(self, gen):
        leaders = gen.generate_civilian_leaders()
        pres = [l for l in leaders if l.role == CivilianRole.PRESIDENT]
        assert len(pres) == 1

    def test_has_sec_def(self, gen):
        leaders = gen.generate_civilian_leaders()
        sd = [l for l in leaders if l.role == CivilianRole.SEC_DEF]
        assert len(sd) == 1

    def test_has_sec_state(self, gen):
        leaders = gen.generate_civilian_leaders()
        ss = [l for l in leaders if l.role == CivilianRole.SEC_STATE]
        assert len(ss) == 1

    def test_has_nsa_director(self, gen):
        leaders = gen.generate_civilian_leaders()
        nsa = [l for l in leaders if l.role == CivilianRole.NSA_DIRECTOR]
        assert len(nsa) == 1

    def test_all_initially_available(self, gen):
        leaders = gen.generate_civilian_leaders()
        for l in leaders:
            assert l.available is True

    def test_none_initially_briefed(self, gen):
        leaders = gen.generate_civilian_leaders()
        for l in leaders:
            assert l.briefed is False

    def test_all_have_unique_ids(self, gen):
        leaders = gen.generate_civilian_leaders()
        ids = [l.id for l in leaders]
        assert len(set(ids)) == 4


# ── Strike Options ────────────────────────────────────────────────────


class TestGenerateStrikeOptions:

    def test_count(self, gen):
        strikes = gen.generate_strike_options()
        assert len(strikes) == 6

    def test_has_diplomatic(self, gen):
        strikes = gen.generate_strike_options()
        dip = [s for s in strikes if s.strike_type == StrikeType.DIPLOMATIC]
        assert len(dip) >= 1

    def test_has_nuclear(self, gen):
        strikes = gen.generate_strike_options()
        nuke = [s for s in strikes if s.strike_type in (
            StrikeType.TACTICAL_NUCLEAR, StrikeType.STRATEGIC_NUCLEAR)]
        assert len(nuke) >= 2

    def test_has_conventional(self, gen):
        strikes = gen.generate_strike_options()
        conv = [s for s in strikes if s.strike_type == StrikeType.CONVENTIONAL]
        assert len(conv) >= 1

    def test_has_cyber(self, gen):
        strikes = gen.generate_strike_options()
        cyber = [s for s in strikes if s.strike_type == StrikeType.CYBER_COUNTER]
        assert len(cyber) >= 1

    def test_diplomatic_zero_casualties(self, gen):
        strikes = gen.generate_strike_options()
        dip = [s for s in strikes if s.strike_type == StrikeType.DIPLOMATIC]
        for s in dip:
            assert s.estimated_casualties == 0

    def test_nuclear_high_casualties(self, gen):
        strikes = gen.generate_strike_options()
        nuke = [s for s in strikes if s.strike_type == StrikeType.STRATEGIC_NUCLEAR]
        for s in nuke:
            assert s.estimated_casualties > 10000

    def test_all_have_unique_ids(self, gen):
        strikes = gen.generate_strike_options()
        ids = [s.id for s in strikes]
        assert len(set(ids)) == 6

    def test_casualties_increase_with_severity(self, gen):
        strikes = gen.generate_strike_options()
        # Sort by strike type severity
        diplomatic = [s for s in strikes if s.strike_type == StrikeType.DIPLOMATIC]
        nuclear = [s for s in strikes if s.strike_type == StrikeType.STRATEGIC_NUCLEAR]
        assert all(d.estimated_casualties < n.estimated_casualties
                   for d in diplomatic for n in nuclear)


# ── Communication Channels ────────────────────────────────────────────


class TestGenerateChannels:

    def test_count(self, gen):
        channels = gen.generate_channels()
        assert len(channels) == 4

    def test_has_hotline(self, gen):
        channels = gen.generate_channels()
        hot = [c for c in channels if c.channel_type == ChannelType.HOTLINE]
        assert len(hot) >= 1

    def test_has_diplomatic(self, gen):
        channels = gen.generate_channels()
        dip = [c for c in channels if c.channel_type == ChannelType.DIPLOMATIC]
        assert len(dip) >= 1

    def test_all_initially_active(self, gen):
        channels = gen.generate_channels()
        for c in channels:
            assert c.active is True

    def test_all_zero_messages(self, gen):
        channels = gen.generate_channels()
        for c in channels:
            assert c.messages_sent == 0

    def test_all_have_unique_ids(self, gen):
        channels = gen.generate_channels()
        ids = [c.id for c in channels]
        assert len(set(ids)) == 4


# ── Availability Schedule ─────────────────────────────────────────────


class TestAvailabilitySchedule:

    def test_has_entries(self, gen):
        sched = gen.generate_availability_schedule()
        assert len(sched) >= 3

    def test_president_unavailable_windows(self, gen):
        sched = gen.generate_availability_schedule()
        pres_windows = sched.get("leader_001", [])
        assert len(pres_windows) >= 1

    def test_windows_are_tuples(self, gen):
        sched = gen.generate_availability_schedule()
        for lid, windows in sched.items():
            for start, end in windows:
                assert isinstance(start, int)
                assert isinstance(end, int)
                assert start < end


# ── Dilemma Schedule ──────────────────────────────────────────────────


class TestDilemmaSchedule:

    def test_count(self, gen):
        sched = gen.generate_dilemma_schedule()
        assert len(sched) == 8

    def test_all_hours_are_ints(self, gen):
        sched = gen.generate_dilemma_schedule()
        for hour in sched:
            assert isinstance(hour, int)

    def test_all_have_dilemma_type(self, gen):
        sched = gen.generate_dilemma_schedule()
        for hour, (dtype, tid, desc) in sched.items():
            assert isinstance(dtype, DilemmaType)

    def test_all_reference_threats(self, gen):
        sched = gen.generate_dilemma_schedule()
        for hour, (dtype, tid, desc) in sched.items():
            assert tid.startswith("threat_")

    def test_all_have_descriptions(self, gen):
        sched = gen.generate_dilemma_schedule()
        for hour, (dtype, tid, desc) in sched.items():
            assert len(desc) > 10


# ── Full Generation ───────────────────────────────────────────────────


class TestGenerateAll:

    def test_returns_all_keys(self, gen):
        data = gen.generate_all()
        assert "threats" in data
        assert "advisors" in data
        assert "civilian_leaders" in data
        assert "strike_options" in data
        assert "channels" in data
        assert "availability_schedule" in data
        assert "dilemma_schedule" in data

    def test_counts(self, gen):
        data = gen.generate_all()
        assert len(data["threats"]) == 8
        assert len(data["advisors"]) == 5
        assert len(data["civilian_leaders"]) == 4
        assert len(data["strike_options"]) == 6
        assert len(data["channels"]) == 4

    def test_deterministic(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        assert len(d1["threats"]) == len(d2["threats"])
        assert [t.id for t in d1["threats"]] == [t.id for t in d2["threats"]]
