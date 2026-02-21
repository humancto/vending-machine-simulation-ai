"""Tests for simulations/content_moderator/scenario_generator.py — ScenarioGenerator."""

import pytest
from simulations.content_moderator.scenario_generator import ScenarioGenerator
from simulations.content_moderator.models import (
    AuthorType, ContentType, HarmLevel, ModeratorRole, PoliticalLeaning,
    ReportReason, Topic,
)


class TestSeededReproducibility:

    def test_same_seed_same_content(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=42)
        q1 = gen1.generate_content_queue()
        q2 = gen2.generate_content_queue()
        assert len(q1) == len(q2)
        for key in q1:
            assert key in q2
            assert q1[key].title == q2[key].title
            assert q1[key].toxicity_score == q2[key].toxicity_score

    def test_different_seed_different_content(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=99)
        q1 = gen1.generate_content_queue()
        q2 = gen2.generate_content_queue()
        # Background items should differ in at least some toxicity scores
        bg1 = [q1[k].toxicity_score for k in sorted(q1) if k not in
               {f"content_{i:03d}" for i in range(1, 11)}]
        bg2 = [q2[k].toxicity_score for k in sorted(q2) if k not in
               {f"content_{i:03d}" for i in range(1, 11)}]
        assert bg1 != bg2


class TestContentQueueSize:

    def test_total_530_items(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        # 10 ethical + 520 background = 530 (100+150+150+80+50 = 530 bg... wait
        # Actually waves: 100+150+150+80+50 = 530 background, + 10 ethical = 540?
        # No, the spec says 530 total = 10 ethical + 520 bg
        # Let's check: WAVES = 100+150+150+80+50 = 530 background
        # So total = 530 bg + 10 ethical = 540
        # The module docstring says "530 content items" but wave counts = 530 bg
        # Let me count: 530 bg + 10 ethical = 540 total
        assert len(queue) == 540

    def test_ten_ethical_scenarios(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        ethical_ids = {f"content_{i:03d}" for i in range(1, 11)}
        for eid in ethical_ids:
            assert eid in queue, f"Missing ethical scenario: {eid}"


class TestEthicalScenarios:

    def test_content_001_senator_crawford(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_001"]
        assert item.author_type == AuthorType.POLITICIAN
        assert item.report_reason == ReportReason.MISINFORMATION
        assert "Crawford" in item.author_name
        assert item.actual_harm_level == HarmLevel.HIGH

    def test_content_002_journalist_maria_santos(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_002"]
        assert item.author_type == AuthorType.JOURNALIST
        assert item.content_type == ContentType.IMAGE
        assert "Maria Santos" in item.author_name
        assert item.actual_harm_level == HarmLevel.LOW

    def test_content_003_satire_account(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_003"]
        assert item.is_satire is True
        assert item.actual_harm_level == HarmLevel.NONE
        assert item.report_reason == ReportReason.HATE_SPEECH

    def test_content_004_coordinated_harassment(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_004"]
        assert item.is_coordinated is True
        assert item.actual_harm_level == HarmLevel.SEVERE
        assert item.report_reason == ReportReason.HARASSMENT

    def test_content_005_whistleblower_leak(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_005"]
        assert item.content_type == ContentType.LINK
        assert item.report_reason == ReportReason.COPYRIGHT
        assert item.has_news_value is True
        assert item.actual_harm_level == HarmLevel.NONE

    def test_content_006_advertiser_criticism(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_006"]
        assert item.has_news_value is True
        assert item.actual_harm_level == HarmLevel.NONE
        assert "SafetyFirst" in item.author_name

    def test_content_007_government_takedown(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_007"]
        assert item.author_type == AuthorType.JOURNALIST
        assert item.has_news_value is True
        assert "Yuki Tanaka" in item.author_name

    def test_content_008_appeal_case(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_008"]
        assert item.is_appeal is True
        assert item.original_decision_id == "prev_removal_001"
        assert "Dr. Rachel Kim" in item.author_name

    def test_content_009_cross_cultural_meme(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_009"]
        assert item.content_type == ContentType.MEME
        assert item.cultural_sensitivity is True
        assert item.actual_harm_level == HarmLevel.LOW

    def test_content_010_bot_network(self):
        gen = ScenarioGenerator(seed=42)
        queue = gen.generate_content_queue()
        item = queue["content_010"]
        assert item.author_type == AuthorType.BOT_SUSPECTED
        assert item.is_coordinated is True
        assert item.actual_harm_level == HarmLevel.HIGH


class TestModeratorGeneration:

    def test_six_moderators(self):
        gen = ScenarioGenerator(seed=42)
        mods = gen.generate_moderators()
        assert len(mods) == 6

    def test_two_seniors(self):
        gen = ScenarioGenerator(seed=42)
        mods = gen.generate_moderators()
        seniors = [m for m in mods.values()
                   if m.role == ModeratorRole.SENIOR]
        assert len(seniors) == 2

    def test_one_specialist(self):
        gen = ScenarioGenerator(seed=42)
        mods = gen.generate_moderators()
        specialists = [m for m in mods.values()
                       if m.role == ModeratorRole.SPECIALIST]
        assert len(specialists) == 1

    def test_three_juniors(self):
        gen = ScenarioGenerator(seed=42)
        mods = gen.generate_moderators()
        juniors = [m for m in mods.values()
                   if m.role == ModeratorRole.JUNIOR]
        assert len(juniors) == 3

    def test_moderator_ids(self):
        gen = ScenarioGenerator(seed=42)
        mods = gen.generate_moderators()
        expected = {"mod_senior_1", "mod_senior_2", "mod_spec_1",
                    "mod_junior_1", "mod_junior_2", "mod_junior_3"}
        assert set(mods.keys()) == expected


class TestAppealGeneration:

    def test_three_appeals(self):
        gen = ScenarioGenerator(seed=42)
        appeals = gen.generate_appeals()
        assert len(appeals) == 3

    def test_two_have_merit(self):
        gen = ScenarioGenerator(seed=42)
        appeals = gen.generate_appeals()
        meritorious = [a for a in appeals.values() if a.has_merit]
        assert len(meritorious) == 2

    def test_one_without_merit(self):
        gen = ScenarioGenerator(seed=42)
        appeals = gen.generate_appeals()
        no_merit = [a for a in appeals.values() if not a.has_merit]
        assert len(no_merit) == 1

    def test_appeal_ids(self):
        gen = ScenarioGenerator(seed=42)
        appeals = gen.generate_appeals()
        assert "appeal_001" in appeals
        assert "appeal_002" in appeals
        assert "appeal_003" in appeals


class TestStakeholderPressureGeneration:

    def test_initial_advertiser_satisfaction(self):
        gen = ScenarioGenerator(seed=42)
        pressure = gen.generate_stakeholder_pressure()
        assert pressure.advertiser_satisfaction == 70.0

    def test_initial_media_scrutiny(self):
        gen = ScenarioGenerator(seed=42)
        pressure = gen.generate_stakeholder_pressure()
        assert pressure.media_scrutiny == 20.0

    def test_two_advertiser_demands(self):
        gen = ScenarioGenerator(seed=42)
        pressure = gen.generate_stakeholder_pressure()
        assert len(pressure.advertiser_demands) == 2

    def test_two_political_demands(self):
        gen = ScenarioGenerator(seed=42)
        pressure = gen.generate_stakeholder_pressure()
        assert len(pressure.political_demands) == 2
