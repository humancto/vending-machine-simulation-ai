"""Tests for simulations/news_editor/scenario_generator.py."""

import random
import pytest
from simulations.news_editor.scenario_generator import ScenarioGenerator
from simulations.news_editor.models import (
    DilemmaType, PressureType, SourceReliability, StoryStatus,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


class TestGenerateStories:

    def test_returns_list(self, gen):
        stories = gen.generate_stories()
        assert isinstance(stories, list)

    def test_has_twelve_stories(self, gen):
        stories = gen.generate_stories()
        assert len(stories) == 12

    def test_all_have_ids(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert s.id
            assert isinstance(s.id, str)

    def test_all_have_headlines(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert s.headline
            assert len(s.headline) > 5

    def test_all_have_content_summary(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert s.content_summary
            assert len(s.content_summary) > 10

    def test_unique_ids(self, gen):
        stories = gen.generate_stories()
        ids = [s.id for s in stories]
        assert len(ids) == len(set(ids))

    def test_main_scandal_exists(self, gen):
        stories = gen.generate_stories()
        main = [s for s in stories if s.id == "story_main_scandal"]
        assert len(main) == 1
        assert main[0].public_interest_level == 10

    def test_affair_rumor_low_accuracy(self, gen):
        stories = gen.generate_stories()
        affair = [s for s in stories if s.id == "story_affair_rumor"]
        assert len(affair) == 1
        assert affair[0].accuracy_score < 0.5

    def test_forged_document_needs_retraction(self, gen):
        stories = gen.generate_stories()
        forged = [s for s in stories if s.id == "story_forged_document"]
        assert len(forged) == 1
        assert forged[0].retraction_needed is True

    def test_all_start_developing(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert s.status == StoryStatus.DEVELOPING

    def test_public_interest_levels_in_range(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert 1 <= s.public_interest_level <= 10

    def test_sensationalism_levels_in_range(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert 1 <= s.sensationalism_level <= 10

    def test_accuracy_scores_in_range(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert 0.0 <= s.accuracy_score <= 1.0

    def test_legal_risk_in_range(self, gen):
        stories = gen.generate_stories()
        for s in stories:
            assert 0.0 <= s.legal_risk <= 1.0


class TestGenerateSources:

    def test_returns_list(self, gen):
        sources = gen.generate_sources()
        assert isinstance(sources, list)

    def test_has_ten_sources(self, gen):
        sources = gen.generate_sources()
        assert len(sources) == 10

    def test_all_have_ids(self, gen):
        sources = gen.generate_sources()
        for s in sources:
            assert s.id
            assert isinstance(s.id, str)

    def test_unique_ids(self, gen):
        sources = gen.generate_sources()
        ids = [s.id for s in sources]
        assert len(ids) == len(set(ids))

    def test_whistleblower_exists(self, gen):
        sources = gen.generate_sources()
        wb = [s for s in sources if s.id == "src_whistleblower"]
        assert len(wb) == 1
        assert wb[0].name == "Sarah Park"
        assert wb[0].needs_protection is True

    def test_anonymous_tipster_unverified(self, gen):
        sources = gen.generate_sources()
        anon = [s for s in sources if s.id == "src_anonymous_tipster"]
        assert len(anon) == 1
        assert anon[0].reliability == SourceReliability.UNVERIFIED

    def test_court_docs_verified(self, gen):
        sources = gen.generate_sources()
        docs = [s for s in sources if s.id == "src_court_docs"]
        assert len(docs) == 1
        assert docs[0].reliability == SourceReliability.VERIFIED

    def test_all_have_types(self, gen):
        sources = gen.generate_sources()
        valid_types = {"WHISTLEBLOWER", "OFFICIAL", "ANONYMOUS",
                       "DOCUMENT", "LEAKED_RECORDING"}
        for s in sources:
            assert s.type in valid_types


class TestGenerateReporters:

    def test_returns_list(self, gen):
        reporters = gen.generate_reporters()
        assert isinstance(reporters, list)

    def test_has_six_reporters(self, gen):
        reporters = gen.generate_reporters()
        assert len(reporters) == 6

    def test_unique_ids(self, gen):
        reporters = gen.generate_reporters()
        ids = [r.id for r in reporters]
        assert len(ids) == len(set(ids))

    def test_skill_levels_in_range(self, gen):
        reporters = gen.generate_reporters()
        for r in reporters:
            assert 0 <= r.skill_level <= 100

    def test_intern_has_low_skill(self, gen):
        reporters = gen.generate_reporters()
        intern = [r for r in reporters if r.id == "rep_intern_alex"]
        assert len(intern) == 1
        assert intern[0].skill_level < 50

    def test_all_have_names(self, gen):
        reporters = gen.generate_reporters()
        for r in reporters:
            assert r.name
            assert len(r.name) > 2

    def test_fatigue_in_range(self, gen):
        reporters = gen.generate_reporters()
        for r in reporters:
            assert 0 <= r.fatigue <= 100

    def test_morale_in_range(self, gen):
        reporters = gen.generate_reporters()
        for r in reporters:
            assert 0 <= r.morale <= 100


class TestGenerateAdvertisers:

    def test_returns_list(self, gen):
        advertisers = gen.generate_advertisers()
        assert isinstance(advertisers, list)

    def test_has_four_advertisers(self, gen):
        advertisers = gen.generate_advertisers()
        assert len(advertisers) == 4

    def test_unique_ids(self, gen):
        advertisers = gen.generate_advertisers()
        ids = [a.id for a in advertisers]
        assert len(ids) == len(set(ids))

    def test_two_pro_governor(self, gen):
        advertisers = gen.generate_advertisers()
        pro = [a for a in advertisers if a.political_alignment == "pro_governor"]
        assert len(pro) == 2

    def test_two_neutral(self, gen):
        advertisers = gen.generate_advertisers()
        neutral = [a for a in advertisers if a.political_alignment == "neutral"]
        assert len(neutral) == 2

    def test_all_have_revenue(self, gen):
        advertisers = gen.generate_advertisers()
        for a in advertisers:
            assert a.revenue_per_day > 0

    def test_apex_is_biggest(self, gen):
        advertisers = gen.generate_advertisers()
        apex = [a for a in advertisers if a.id == "adv_apex"]
        assert len(apex) == 1
        assert apex[0].revenue_per_day >= max(
            a.revenue_per_day for a in advertisers if a.id != "adv_apex")


class TestGenerateDilemmas:

    def test_returns_list(self, gen):
        dilemmas = gen.generate_dilemmas()
        assert isinstance(dilemmas, list)

    def test_has_ten_dilemmas(self, gen):
        dilemmas = gen.generate_dilemmas()
        assert len(dilemmas) == 10

    def test_unique_ids(self, gen):
        dilemmas = gen.generate_dilemmas()
        ids = [d.id for d in dilemmas]
        assert len(ids) == len(set(ids))

    def test_all_have_hours(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert 1 <= d.hour <= 48

    def test_competitor_scoop_at_hour_3(self, gen):
        dilemmas = gen.generate_dilemmas()
        scoop = [d for d in dilemmas if d.id == "dilemma_competitor_scoop"]
        assert len(scoop) == 1
        assert scoop[0].hour == 3

    def test_all_have_descriptions(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert d.description
            assert len(d.description) > 10

    def test_all_have_temptation_actions(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert d.temptation_action

    def test_none_triggered_initially(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert d.triggered is False

    def test_none_resolved_initially(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert d.resolved is False


class TestGeneratePressures:

    def test_returns_list(self, gen):
        pressures = gen.generate_pressures()
        assert isinstance(pressures, list)

    def test_has_six_pressures(self, gen):
        pressures = gen.generate_pressures()
        assert len(pressures) == 6

    def test_unique_ids(self, gen):
        pressures = gen.generate_pressures()
        ids = [p.id for p in pressures]
        assert len(ids) == len(set(ids))

    def test_all_have_types(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert isinstance(p.type, PressureType)

    def test_all_have_entities(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert p.from_entity

    def test_legal_pressure_exists(self, gen):
        pressures = gen.generate_pressures()
        legal = [p for p in pressures if p.type == PressureType.LEGAL]
        assert len(legal) >= 1

    def test_none_resolved_initially(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert p.resolved is False


class TestDeterminism:

    def test_same_seed_same_stories(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        s1 = gen1.generate_stories()
        s2 = gen2.generate_stories()
        assert len(s1) == len(s2)
        for a, b in zip(s1, s2):
            assert a.id == b.id
            assert a.headline == b.headline

    def test_same_seed_same_sources(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        s1 = gen1.generate_sources()
        s2 = gen2.generate_sources()
        for a, b in zip(s1, s2):
            assert a.id == b.id
            assert a.name == b.name

    def test_same_seed_same_reporters(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        r1 = gen1.generate_reporters()
        r2 = gen2.generate_reporters()
        for a, b in zip(r1, r2):
            assert a.id == b.id
            assert a.skill_level == b.skill_level
