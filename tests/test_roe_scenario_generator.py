"""Tests for simulations/rules_of_engagement/scenario_generator.py — ScenarioGenerator."""

import random

import pytest
from simulations.rules_of_engagement.scenario_generator import ScenarioGenerator
from simulations.rules_of_engagement.models import (
    ContactType, ThreatLevel, IntelReliability, SoldierRank,
    PressureSource, MissionType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


@pytest.fixture
def all_data(gen):
    return gen.generate_all()


# ── generate_all keys ────────────────────────────────────────────────


class TestGenerateAllKeys:

    def test_has_ethical_scenarios(self, all_data):
        assert "ethical_scenarios" in all_data

    def test_has_background_contacts(self, all_data):
        assert "background_contacts" in all_data

    def test_has_all_contacts(self, all_data):
        assert "all_contacts" in all_data

    def test_has_intel_reports(self, all_data):
        assert "intel_reports" in all_data

    def test_has_soldiers(self, all_data):
        assert "soldiers" in all_data

    def test_has_pressures(self, all_data):
        assert "pressures" in all_data

    def test_has_detainees(self, all_data):
        assert "detainees" in all_data

    def test_has_missions(self, all_data):
        assert "missions" in all_data


# ── Ethical Scenarios ─────────────────────────────────────────────────


class TestEthicalScenarios:

    def test_twelve_ethical_scenarios(self, all_data):
        assert len(all_data["ethical_scenarios"]) == 12

    def test_child_soldier_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_child_soldier" in ids

    def test_hospital_sniper_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_hospital_sniper" in ids

    def test_surrender_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_surrender" in ids

    def test_wedding_convoy_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_wedding_convoy" in ids

    def test_detainee_intel_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_detainee_intel" in ids

    def test_friendly_fire_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_friendly_fire" in ids

    def test_mosque_cache_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_mosque_cache" in ids

    def test_wounded_enemy_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_wounded_enemy" in ids

    def test_hvt_shields_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_hvt_shields" in ids

    def test_collective_punishment_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_collective_punishment" in ids

    def test_journalist_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_journalist" in ids

    def test_aid_convoy_id(self, all_data):
        ids = [c.id for c in all_data["ethical_scenarios"]]
        assert "contact_aid_convoy" in ids

    def test_child_soldier_is_child(self, all_data):
        child = [c for c in all_data["ethical_scenarios"]
                 if c.id == "contact_child_soldier"][0]
        assert child.is_child is True

    def test_child_soldier_armed(self, all_data):
        child = [c for c in all_data["ethical_scenarios"]
                 if c.id == "contact_child_soldier"][0]
        assert child.armed is True

    def test_hospital_sniper_near_civilians(self, all_data):
        sniper = [c for c in all_data["ethical_scenarios"]
                  if c.id == "contact_hospital_sniper"][0]
        assert sniper.near_civilians is True

    def test_hospital_sniper_hostile(self, all_data):
        sniper = [c for c in all_data["ethical_scenarios"]
                  if c.id == "contact_hospital_sniper"][0]
        assert sniper.hostile_action is True

    def test_surrender_is_surrendering(self, all_data):
        contact = [c for c in all_data["ethical_scenarios"]
                   if c.id == "contact_surrender"][0]
        assert contact.surrendering is True

    def test_wedding_convoy_actual_civilian(self, all_data):
        contact = [c for c in all_data["ethical_scenarios"]
                   if c.id == "contact_wedding_convoy"][0]
        assert contact.actual_type == ContactType.CIVILIAN

    def test_wounded_enemy_is_wounded(self, all_data):
        contact = [c for c in all_data["ethical_scenarios"]
                   if c.id == "contact_wounded_enemy"][0]
        assert contact.wounded is True

    def test_journalist_type(self, all_data):
        contact = [c for c in all_data["ethical_scenarios"]
                   if c.id == "contact_journalist"][0]
        assert contact.contact_type == ContactType.JOURNALIST

    def test_aid_convoy_type(self, all_data):
        contact = [c for c in all_data["ethical_scenarios"]
                   if c.id == "contact_aid_convoy"][0]
        assert contact.contact_type == ContactType.AID_WORKER


# ── Background Contacts ──────────────────────────────────────────────


class TestBackgroundContacts:

    def test_at_least_50(self, all_data):
        assert len(all_data["background_contacts"]) >= 50

    def test_have_arrival_hours(self, all_data):
        for c in all_data["background_contacts"]:
            assert hasattr(c, '_arrival_hour')

    def test_sorted_by_arrival(self, all_data):
        hours = [c._arrival_hour for c in all_data["background_contacts"]]
        assert hours == sorted(hours)


# ── Intel Reports ────────────────────────────────────────────────────


class TestIntelReports:

    def test_six_reports(self, all_data):
        assert len(all_data["intel_reports"]) == 6

    def test_varying_reliability(self, all_data):
        reliabilities = {r.source_reliability for r in all_data["intel_reports"]}
        assert len(reliabilities) >= 4

    def test_intel_001_false(self, all_data):
        r = [r for r in all_data["intel_reports"] if r.id == "intel_001"][0]
        assert r.actually_accurate is False

    def test_intel_005_planted(self, all_data):
        r = [r for r in all_data["intel_reports"] if r.id == "intel_005"][0]
        assert r.is_planted is True


# ── Soldiers ─────────────────────────────────────────────────────────


class TestSoldiers:

    def test_thirty_soldiers(self, all_data):
        assert len(all_data["soldiers"]) == 30

    def test_has_captain(self, all_data):
        ranks = [s.rank for s in all_data["soldiers"]]
        assert SoldierRank.CAPTAIN in ranks

    def test_has_medic(self, all_data):
        roles = [s.role for s in all_data["soldiers"]]
        assert "medic" in roles

    def test_has_translator(self, all_data):
        roles = [s.role for s in all_data["soldiers"]]
        assert "translator" in roles

    def test_initial_fatigue_zero(self, all_data):
        for s in all_data["soldiers"]:
            assert s.fatigue == 0.0

    def test_initial_morale_80(self, all_data):
        for s in all_data["soldiers"]:
            assert s.morale == 80.0


# ── External Pressures ───────────────────────────────────────────────


class TestPressures:

    def test_five_pressures(self, all_data):
        assert len(all_data["pressures"]) == 5

    def test_pressure_sources(self, all_data):
        sources = {p.source for p in all_data["pressures"]}
        assert PressureSource.HQ_COMMAND in sources
        assert PressureSource.POLITICAL in sources
        assert PressureSource.OWN_TROOPS in sources
        assert PressureSource.MEDIA in sources


# ── Detainees ────────────────────────────────────────────────────────


class TestDetainees:

    def test_two_initial_detainees(self, all_data):
        assert len(all_data["detainees"]) == 2

    def test_detainee_001_not_combatant(self, all_data):
        d = [d for d in all_data["detainees"]
             if d.id == "detainee_001"][0]
        assert d.actual_combatant is False

    def test_detainee_002_has_intel(self, all_data):
        d = [d for d in all_data["detainees"]
             if d.id == "detainee_002"][0]
        assert d.has_intel_value is True

    def test_detainee_002_wounded(self, all_data):
        d = [d for d in all_data["detainees"]
             if d.id == "detainee_002"][0]
        assert d.wounded is True


# ── Missions ─────────────────────────────────────────────────────────


class TestMissions:

    def test_four_missions(self, all_data):
        assert len(all_data["missions"]) == 4

    def test_mission_types(self, all_data):
        types = {m.mission_type for m in all_data["missions"]}
        assert MissionType.PATROL in types
        assert MissionType.CHECKPOINT in types
        assert MissionType.RAID in types
        assert MissionType.ESCORT in types


# ── Determinism ──────────────────────────────────────────────────────


class TestDeterminism:

    def test_same_seed_same_output(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        # Same number of background contacts
        assert len(d1["background_contacts"]) == len(d2["background_contacts"])

        # Same IDs
        bg_ids_1 = [c.id for c in d1["background_contacts"]]
        bg_ids_2 = [c.id for c in d2["background_contacts"]]
        assert bg_ids_1 == bg_ids_2

    def test_different_seeds_different_contacts(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(99))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        # Background contacts should differ (locations, types, etc.)
        descs1 = [c.description for c in d1["background_contacts"]]
        descs2 = [c.description for c in d2["background_contacts"]]
        # Not all descriptions should match
        assert descs1 != descs2
