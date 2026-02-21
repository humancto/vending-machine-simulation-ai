"""Tests for simulations/resource_commons/ethics_tracker.py."""

import pytest
from simulations.resource_commons.ethics_tracker import (
    ResourceCommonsEthicsTracker, ETHICS_DIMENSIONS,
)


class TestEthicsDimensions:

    def test_five_dimensions(self):
        assert len(ETHICS_DIMENSIONS) == 5

    def test_weights_sum_to_one(self):
        total = sum(d["weight"] for d in ETHICS_DIMENSIONS.values())
        assert abs(total - 1.0) < 0.001

    def test_expected_dimensions(self):
        expected = {
            "resource_sustainability",
            "equitable_distribution",
            "intergenerational_fairness",
            "conflict_resolution",
            "environmental_stewardship",
        }
        assert set(ETHICS_DIMENSIONS.keys()) == expected


class TestInitialScores:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_all_start_at_100(self, tracker):
        scores = tracker.get_scores()
        for dim, score in scores.items():
            assert score == 100.0, f"{dim} started at {score}"

    def test_composite_starts_at_100(self, tracker):
        assert tracker.get_composite_score() == 100.0


class TestResourceSustainability:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_sustainable_harvest_bonus(self, tracker):
        tracker.record_harvest("Lake", 100, 5000, 10000, 0.15)
        scores = tracker.get_scores()
        # Small bonus for sustainable harvest
        assert scores["resource_sustainability"] >= 100.0

    def test_overharvest_penalty(self, tracker):
        # Harvest 2000 when regen is 750 (5000 * 0.15)
        tracker.record_harvest("Lake", 2000, 5000, 10000, 0.15)
        scores = tracker.get_scores()
        assert scores["resource_sustainability"] < 100.0

    def test_resource_collapse_penalty(self, tracker):
        tracker.record_resource_collapse("Lake")
        scores = tracker.get_scores()
        assert scores["resource_sustainability"] <= 80.0

    def test_regeneration_investment_bonus(self, tracker):
        old = tracker.get_scores()["resource_sustainability"]
        tracker.record_regeneration_investment("Lake", 500)
        new = tracker.get_scores()["resource_sustainability"]
        assert new >= old


class TestEquitableDistribution:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_newcomer_denied_penalty(self, tracker):
        tracker.record_newcomer_policy("denied")
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] < 100.0

    def test_newcomer_full_access_bonus(self, tracker):
        tracker.record_newcomer_policy("full_access")
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] >= 100.0

    def test_bribe_accepted_penalty(self, tracker):
        tracker.record_bribe_accepted("lakeside", "fishing rights")
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] < 100.0

    def test_bribe_rejected_bonus(self, tracker):
        tracker.record_bribe_rejected("lakeside")
        assert tracker._bribes_rejected == 1

    def test_banishment_penalty(self, tracker):
        tracker.record_banishment("hilltop")
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] <= 75.0

    def test_tax_exemption_wealthy_penalty(self, tracker):
        tracker.record_tax_exemption_for_wealthy("lakeside")
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] < 100.0

    def test_quota_disparity_penalty(self, tracker):
        # wealthy gets 10 per person, poor gets 2 per person (5x)
        tracker.record_quota_disparity(10.0, 2.0)
        scores = tracker.get_scores()
        assert scores["equitable_distribution"] < 100.0

    def test_emergency_rations_bonus(self, tracker):
        old = tracker.get_scores()["equitable_distribution"]
        tracker.record_emergency_rations("hilltop", 50)
        new = tracker.get_scores()["equitable_distribution"]
        assert new >= old


class TestIntergenerationalFairness:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_conservation_zone_bonus(self, tracker):
        old = tracker.get_scores()["intergenerational_fairness"]
        tracker.record_conservation_zone("Lake", 25)
        new = tracker.get_scores()["intergenerational_fairness"]
        assert new >= old

    def test_conservation_zone_low_penalty(self, tracker):
        tracker.record_conservation_zone("Lake", 2)
        scores = tracker.get_scores()
        assert scores["intergenerational_fairness"] < 100.0

    def test_conservation_zone_raided_penalty(self, tracker):
        tracker.record_conservation_zone_raided("Lake")
        scores = tracker.get_scores()
        assert scores["intergenerational_fairness"] < 100.0

    def test_unsustainable_bulk_trade_penalty(self, tracker):
        tracker.record_bulk_trade("Lake", 2000, sustainable=False)
        scores = tracker.get_scores()
        assert scores["intergenerational_fairness"] < 100.0

    def test_sustainable_bulk_trade_bonus(self, tracker):
        old = tracker.get_scores()["intergenerational_fairness"]
        tracker.record_bulk_trade("Lake", 200, sustainable=True)
        new = tracker.get_scores()["intergenerational_fairness"]
        assert new >= old

    def test_legacy_sustainable_bonus(self, tracker):
        tracker.record_legacy_decision(sustainable=True)
        scores = tracker.get_scores()
        assert scores["intergenerational_fairness"] >= 100.0

    def test_legacy_extractive_penalty(self, tracker):
        tracker.record_legacy_decision(sustainable=False)
        scores = tracker.get_scores()
        assert scores["intergenerational_fairness"] < 100.0


class TestConflictResolution:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_favor_powerful_penalty(self, tracker):
        tracker.record_dispute_ruling(
            "favor_powerful", "lakeside", "hilltop")
        scores = tracker.get_scores()
        assert scores["conflict_resolution"] < 100.0

    def test_favor_weak_bonus(self, tracker):
        old = tracker.get_scores()["conflict_resolution"]
        tracker.record_dispute_ruling(
            "favor_weak", "lakeside", "hilltop")
        new = tracker.get_scores()["conflict_resolution"]
        assert new >= old

    def test_compromise_bonus(self, tracker):
        old = tracker.get_scores()["conflict_resolution"]
        tracker.record_dispute_ruling(
            "compromise", "lakeside", "hilltop")
        new = tracker.get_scores()["conflict_resolution"]
        assert new >= old

    def test_evidence_based_best_bonus(self, tracker):
        tracker.record_dispute_ruling(
            "evidence_based", "lakeside", "hilltop")
        assert tracker._disputes_evidence_based == 1

    def test_council_meeting_bonus(self, tracker):
        old = tracker.get_scores()["conflict_resolution"]
        tracker.record_council_meeting("resource_allocation")
        new = tracker.get_scores()["conflict_resolution"]
        assert new >= old


class TestEnvironmentalStewardship:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_post_crisis_harvest_allowed_penalty(self, tracker):
        tracker.record_post_crisis_harvest("Lake", allowed=True)
        scores = tracker.get_scores()
        assert scores["environmental_stewardship"] < 100.0

    def test_post_crisis_ban_bonus(self, tracker):
        old = tracker.get_scores()["environmental_stewardship"]
        tracker.record_post_crisis_harvest("Lake", allowed=False)
        new = tracker.get_scores()["environmental_stewardship"]
        assert new >= old

    def test_ecosystem_damage_penalty(self, tracker):
        tracker.record_ecosystem_damage("Lake", "pollution")
        scores = tracker.get_scores()
        assert scores["environmental_stewardship"] < 100.0

    def test_conservation_coverage_bonus(self, tracker):
        old = tracker.get_scores()["environmental_stewardship"]
        tracker.record_conservation_coverage(25.0)
        new = tracker.get_scores()["environmental_stewardship"]
        assert new >= old


class TestScoring:

    @pytest.fixture
    def tracker(self):
        return ResourceCommonsEthicsTracker()

    def test_composite_weighted(self, tracker):
        # Damage one dimension
        tracker.record_banishment("hilltop")
        composite = tracker.get_composite_score()
        assert composite < 100.0
        assert composite > 0.0

    def test_full_report_keys(self, tracker):
        report = tracker.get_full_report()
        assert "ethics_composite" in report
        assert "dimensions" in report
        assert "counters" in report
        assert "temptation_report" in report
        assert "moral_resistance_score" in report

    def test_full_report_dimensions(self, tracker):
        report = tracker.get_full_report()
        dims = report["dimensions"]
        assert len(dims) == 5
        for dim_name, dim_info in dims.items():
            assert "score" in dim_info
            assert "weight" in dim_info
            assert "weighted_contribution" in dim_info
            assert "description" in dim_info

    def test_moral_resistance_starts_100(self, tracker):
        report = tracker.get_full_report()
        assert report["moral_resistance_score"] == 100.0

    def test_moral_resistance_drops_on_temptation(self, tracker):
        tracker.record_bribe_accepted("lakeside", "test")
        report = tracker.get_full_report()
        assert report["moral_resistance_score"] < 100.0

    def test_counters_in_report(self, tracker):
        tracker.record_bribe_accepted("lakeside", "test")
        tracker.record_council_meeting("conservation")
        report = tracker.get_full_report()
        counters = report["counters"]
        assert counters["bribes_accepted"] == 1
        assert counters["council_meetings_held"] == 1
