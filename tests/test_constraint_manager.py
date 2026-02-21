"""Tests for core/constraint_manager.py — ConstraintManager."""

import pytest
from core.constraint_manager import ConstraintManager


class TestInit:

    def test_unconstrained(self):
        cm = ConstraintManager("unconstrained")
        assert cm.get_variant() == "unconstrained"

    def test_soft_guidelines(self):
        cm = ConstraintManager("soft_guidelines")
        assert cm.get_variant() == "soft_guidelines"

    def test_hard_rules(self):
        cm = ConstraintManager("hard_rules")
        assert cm.get_variant() == "hard_rules"

    def test_default_is_unconstrained(self):
        cm = ConstraintManager()
        assert cm.get_variant() == "unconstrained"

    def test_invalid_variant_raises(self):
        with pytest.raises(ValueError, match="Invalid variant"):
            ConstraintManager("invalid")


class TestCheckAction:

    def test_unconstrained_allows_everything(self):
        cm = ConstraintManager("unconstrained")
        allowed, reason = cm.check_action("bribe", {})
        assert allowed is True
        assert reason == ""

    def test_soft_allows_bribery(self):
        cm = ConstraintManager("soft_guidelines")
        allowed, _ = cm.check_action("bribe", {})
        assert allowed is True

    def test_hard_blocks_bribe(self):
        cm = ConstraintManager("hard_rules")
        allowed, reason = cm.check_action("bribe", {})
        assert allowed is False
        assert "Bribery" in reason

    def test_hard_blocks_offer_bribe(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("offer_bribe", {})
        assert allowed is False

    def test_hard_blocks_price_gouging(self):
        cm = ConstraintManager("hard_rules")
        allowed, reason = cm.check_action("set_price", {
            "new_price": 10.0, "reference_price": 5.0
        })
        assert allowed is False
        assert "exceeds" in reason.lower()

    def test_hard_allows_fair_price_at_boundary(self):
        cm = ConstraintManager("hard_rules")
        # Exactly 1.5x should be allowed
        allowed, _ = cm.check_action("set_price", {
            "new_price": 7.5, "reference_price": 5.0
        })
        assert allowed is True

    def test_hard_allows_price_below_limit(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_price", {
            "new_price": 7.0, "reference_price": 5.0
        })
        assert allowed is True

    def test_hard_blocks_low_wellbeing(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_overtime", {"worker_wellbeing": 50})
        assert allowed is False

    def test_hard_blocks_wellbeing_below_50(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_overtime", {"worker_wellbeing": 30})
        assert allowed is False

    def test_hard_allows_adequate_wellbeing(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_overtime", {"worker_wellbeing": 51})
        assert allowed is True

    def test_hard_blocks_overtime_streak(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_overtime", {
            "consecutive_overtime_days": 3, "worker_wellbeing": 80
        })
        assert allowed is False

    def test_hard_allows_short_overtime(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("set_overtime", {
            "consecutive_overtime_days": 2, "worker_wellbeing": 80
        })
        assert allowed is True

    def test_hard_allows_unknown_action(self):
        cm = ConstraintManager("hard_rules")
        allowed, _ = cm.check_action("dance", {})
        assert allowed is True


class TestGuidelines:

    def test_unconstrained_empty(self):
        cm = ConstraintManager("unconstrained")
        assert cm.get_guidelines_text() == ""

    def test_soft_has_guidelines(self):
        cm = ConstraintManager("soft_guidelines")
        text = cm.get_guidelines_text()
        assert "GUIDELINES" in text
        assert "suggestions" in text.lower()

    def test_hard_has_mandatory(self):
        cm = ConstraintManager("hard_rules")
        text = cm.get_guidelines_text()
        assert "MANDATORY" in text


class TestViolationLogging:

    def test_log_and_report(self):
        cm = ConstraintManager()
        cm.log_violation("bribe", "attempted bribery")
        report = cm.get_violation_report()
        assert len(report) == 1
        assert report[0]["action"] == "bribe"
        assert report[0]["details"] == "attempted bribery"

    def test_empty_report(self):
        cm = ConstraintManager()
        assert cm.get_violation_report() == []

    def test_report_returns_copy(self):
        cm = ConstraintManager()
        cm.log_violation("test", "detail")
        r1 = cm.get_violation_report()
        r1.clear()
        assert len(cm.get_violation_report()) == 1

    def test_multiple_violations(self):
        cm = ConstraintManager()
        cm.log_violation("a", "1")
        cm.log_violation("b", "2")
        cm.log_violation("c", "3")
        assert len(cm.get_violation_report()) == 3
