"""Tests for core/scoring.py — BehavioralFingerprint and CompositeScorer."""

import pytest
from core.scoring import AXES, BehavioralFingerprint, CompositeScorer


class TestBehavioralFingerprint:

    def test_defaults_to_50(self):
        fp = BehavioralFingerprint()
        for axis in AXES:
            assert fp.get_axis(axis) == 50.0

    def test_custom_values(self):
        fp = BehavioralFingerprint({"ethical_behavior": 80, "risk_tolerance": 20})
        assert fp.get_axis("ethical_behavior") == 80.0
        assert fp.get_axis("risk_tolerance") == 20.0
        assert fp.get_axis("adaptability") == 50.0

    def test_clamping_high(self):
        fp = BehavioralFingerprint({"ethical_behavior": 150})
        assert fp.get_axis("ethical_behavior") == 100.0

    def test_clamping_low(self):
        fp = BehavioralFingerprint({"ethical_behavior": -50})
        assert fp.get_axis("ethical_behavior") == 0.0

    def test_clamping_edge_values(self):
        fp = BehavioralFingerprint({"ethical_behavior": 0, "adaptability": 100})
        assert fp.get_axis("ethical_behavior") == 0.0
        assert fp.get_axis("adaptability") == 100.0

    def test_set_axis(self):
        fp = BehavioralFingerprint()
        fp.set_axis("strategic_depth", 75)
        assert fp.get_axis("strategic_depth") == 75.0

    def test_set_axis_clamps(self):
        fp = BehavioralFingerprint()
        fp.set_axis("strategic_depth", 200)
        assert fp.get_axis("strategic_depth") == 100.0
        fp.set_axis("strategic_depth", -10)
        assert fp.get_axis("strategic_depth") == 0.0

    def test_unknown_axis_get(self):
        fp = BehavioralFingerprint()
        with pytest.raises(KeyError, match="Unknown axis"):
            fp.get_axis("nonexistent_axis")

    def test_unknown_axis_set(self):
        fp = BehavioralFingerprint()
        with pytest.raises(KeyError, match="Unknown axis"):
            fp.set_axis("nonexistent_axis", 50)

    def test_unknown_key_in_constructor_ignored(self):
        fp = BehavioralFingerprint({"unknown_key": 99, "ethical_behavior": 80})
        assert fp.get_axis("ethical_behavior") == 80.0
        assert "unknown_key" not in fp.to_dict()

    def test_to_dict_has_12_axes(self):
        fp = BehavioralFingerprint()
        d = fp.to_dict()
        assert len(d) == 12
        assert all(axis in d for axis in AXES)

    def test_get_summary(self):
        fp = BehavioralFingerprint({"ethical_behavior": 100, "strategic_depth": 0})
        s = fp.get_summary()
        assert "overall_average" in s
        assert "axes" in s
        assert len(s["axes"]) == 12
        # (100 + 0 + 10*50) / 12 = 600/12 = 50.0
        assert s["overall_average"] == 50.0

    def test_float_conversion(self):
        fp = BehavioralFingerprint({"ethical_behavior": 75})
        assert isinstance(fp.get_axis("ethical_behavior"), float)

    def test_all_zeros(self):
        fp = BehavioralFingerprint({axis: 0 for axis in AXES})
        s = fp.get_summary()
        assert s["overall_average"] == 0.0

    def test_all_hundreds(self):
        fp = BehavioralFingerprint({axis: 100 for axis in AXES})
        s = fp.get_summary()
        assert s["overall_average"] == 100.0


class TestCompositeScorer:

    def test_equal_weights(self):
        weights = {axis: 1.0 / 12 for axis in AXES}
        scorer = CompositeScorer(weights)
        fp = BehavioralFingerprint()
        result = scorer.score(fp)
        assert abs(result["total_score"] - 50.0) < 0.1

    def test_single_axis(self):
        scorer = CompositeScorer({"ethical_behavior": 1.0})
        fp = BehavioralFingerprint({"ethical_behavior": 80})
        result = scorer.score(fp)
        assert result["total_score"] == 80.0

    def test_breakdown(self):
        scorer = CompositeScorer({"ethical_behavior": 0.5, "strategic_depth": 0.5})
        fp = BehavioralFingerprint({"ethical_behavior": 100, "strategic_depth": 60})
        result = scorer.score(fp)
        assert result["breakdown"]["ethical_behavior"] == 50.0
        assert result["breakdown"]["strategic_depth"] == 30.0
        assert result["total_score"] == 80.0

    def test_missing_axis_uses_default(self):
        scorer = CompositeScorer({"nonexistent": 1.0})
        fp = BehavioralFingerprint()
        result = scorer.score(fp)
        assert result["total_score"] == 50.0

    def test_raw_included(self):
        scorer = CompositeScorer({"ethical_behavior": 1.0})
        fp = BehavioralFingerprint()
        result = scorer.score(fp)
        assert "raw" in result
        assert len(result["raw"]) == 12

    def test_zero_weight(self):
        scorer = CompositeScorer({"ethical_behavior": 0.0})
        fp = BehavioralFingerprint({"ethical_behavior": 100})
        result = scorer.score(fp)
        assert result["total_score"] == 0.0
