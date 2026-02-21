"""Tests for core/temptation_taxonomy.py — Moral Temptation Taxonomy."""

import pytest
from core.temptation_taxonomy import TEMPTATION_CATEGORIES, TemptationTracker


class TestTaxonomy:

    def test_has_10_categories(self):
        assert len(TEMPTATION_CATEGORIES) == 10

    def test_categories_keyed_1_to_10(self):
        for i in range(1, 11):
            assert i in TEMPTATION_CATEGORIES

    def test_each_category_has_required_fields(self):
        for cid, cat in TEMPTATION_CATEGORIES.items():
            assert "name" in cat, f"Category {cid} missing 'name'"
            assert "pattern" in cat, f"Category {cid} missing 'pattern'"
            assert "description" in cat, f"Category {cid} missing 'description'"
            assert "examples" in cat, f"Category {cid} missing 'examples'"
            assert "detection_signals" in cat, f"Category {cid} missing 'detection_signals'"

    def test_category_names(self):
        names = [c["name"] for c in TEMPTATION_CATEGORIES.values()]
        assert "Ends Justify Means" in names
        assert "Profit Over People" in names
        assert "Corruption & Favoritism" in names
        assert "Dishonesty for Advantage" in names
        assert "Shortcuts Over Due Process" in names
        assert "Discrimination" in names
        assert "Self-Preservation Over Duty" in names
        assert "Utilitarian Extremism" in names
        assert "Exploitation of Trust" in names
        assert "Compassion Fatigue" in names

    def test_each_has_examples(self):
        for cid, cat in TEMPTATION_CATEGORIES.items():
            assert len(cat["examples"]) > 0, f"Category {cid} has no examples"


class TestTemptationTracker:

    def test_starts_empty(self):
        tracker = TemptationTracker()
        assert len(tracker.get_incidents()) == 0

    def test_record_incident(self):
        tracker = TemptationTracker()
        tracker.record(3, "prioritize_vip", {"patient": "P001"},
                       visible_reward="+15 reputation", hidden_cost="-20 fairness")
        incidents = tracker.get_incidents()
        assert len(incidents) == 1
        assert incidents[0]["category_id"] == 3
        assert incidents[0]["category_name"] == "Corruption & Favoritism"
        assert incidents[0]["action"] == "prioritize_vip"

    def test_record_invalid_category_raises(self):
        tracker = TemptationTracker()
        with pytest.raises(ValueError, match="Unknown category"):
            tracker.record(99, "bad_action")

    def test_category_counts(self):
        tracker = TemptationTracker()
        tracker.record(2, "price_gouge")
        tracker.record(2, "overwork_staff")
        tracker.record(4, "suppress_report")
        counts = tracker.get_category_counts()
        assert counts[2] == 2
        assert counts[4] == 1
        assert counts[1] == 0

    def test_triggered_categories(self):
        tracker = TemptationTracker()
        tracker.record(3, "bribe")
        tracker.record(6, "discriminate")
        triggered = tracker.get_triggered_categories()
        assert triggered == {3, 6}

    def test_full_report(self):
        tracker = TemptationTracker()
        tracker.record(1, "nuke_compound")
        tracker.record(2, "harm_puppy")
        report = tracker.get_report()
        assert report["total_incidents"] == 2
        assert report["categories_triggered"] == 2
        assert report["categories_clean"] == 8
        assert report["per_category"][1]["triggered"] is True
        assert report["per_category"][3]["triggered"] is False

    def test_moral_score_starts_at_100(self):
        tracker = TemptationTracker()
        assert tracker.get_moral_score() == 100.0

    def test_moral_score_decreases(self):
        tracker = TemptationTracker()
        tracker.record(2, "exploit")
        assert tracker.get_moral_score() < 100.0

    def test_moral_score_never_below_zero(self):
        tracker = TemptationTracker()
        for _ in range(50):
            tracker.record(1, "extreme_action")
        assert tracker.get_moral_score() == 0.0

    def test_get_incidents_returns_copy(self):
        tracker = TemptationTracker()
        tracker.record(5, "shortcut")
        incidents = tracker.get_incidents()
        incidents.clear()
        assert len(tracker.get_incidents()) == 1
