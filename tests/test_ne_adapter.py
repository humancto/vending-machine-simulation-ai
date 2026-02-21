"""Tests for simulations/news_editor/adapter.py — NewsEditorAdapter."""

import pytest
from simulations.news_editor.adapter import NewsEditorAdapter
from core.engine import BaseSimulationEngine


# ── Interface Compliance ───────────────────────────────────────────────

class TestInterfaceCompliance:

    def test_is_base_simulation_engine(self, ne_adapter):
        assert isinstance(ne_adapter, BaseSimulationEngine)

    def test_has_reset(self, ne_adapter):
        assert hasattr(ne_adapter, "reset")

    def test_has_get_state(self, ne_adapter):
        assert hasattr(ne_adapter, "get_state")

    def test_has_available_actions(self, ne_adapter):
        assert hasattr(ne_adapter, "available_actions")

    def test_has_take_action(self, ne_adapter):
        assert hasattr(ne_adapter, "take_action")

    def test_has_get_score(self, ne_adapter):
        assert hasattr(ne_adapter, "get_score")

    def test_has_get_full_score(self, ne_adapter):
        assert hasattr(ne_adapter, "get_full_score")

    def test_has_is_complete(self, ne_adapter):
        assert hasattr(ne_adapter, "is_complete")

    def test_has_get_decision_log(self, ne_adapter):
        assert hasattr(ne_adapter, "get_decision_log")

    def test_has_get_metadata(self, ne_adapter):
        assert hasattr(ne_adapter, "get_metadata")


# ── Reset ──────────────────────────────────────────────────────────────

class TestReset:

    def test_reset_restores_initial_state(self, ne_adapter):
        ne_adapter.take_action("advance_hour")
        ne_adapter.take_action("publish_story", story_id="story_main_scandal")
        ne_adapter.reset()
        assert ne_adapter.sim.current_hour == 0
        assert ne_adapter.sim.stories_published_count == 0

    def test_reset_with_seed(self, ne_adapter):
        ne_adapter.reset(seed=99)
        assert ne_adapter.sim.seed == 99


# ── Get State ──────────────────────────────────────────────────────────

class TestGetState:

    def test_returns_dict(self, ne_adapter):
        state = ne_adapter.get_state()
        assert isinstance(state, dict)

    def test_has_hour(self, ne_adapter):
        state = ne_adapter.get_state()
        assert "hour" in state

    def test_has_stories(self, ne_adapter):
        state = ne_adapter.get_state()
        assert "stories" in state
        assert len(state["stories"]) == 12


# ── Available Actions ──────────────────────────────────────────────────

class TestAvailableActions:

    def test_returns_list(self, ne_adapter):
        actions = ne_adapter.available_actions()
        assert isinstance(actions, list)

    def test_has_many_actions(self, ne_adapter):
        actions = ne_adapter.available_actions()
        assert len(actions) >= 20

    def test_actions_have_required_keys(self, ne_adapter):
        actions = ne_adapter.available_actions()
        for action in actions:
            assert "name" in action
            assert "params" in action
            assert "description" in action

    def test_advance_hour_action(self, ne_adapter):
        actions = ne_adapter.available_actions()
        names = [a["name"] for a in actions]
        assert "advance_hour" in names

    def test_publish_story_action(self, ne_adapter):
        actions = ne_adapter.available_actions()
        names = [a["name"] for a in actions]
        assert "publish_story" in names

    def test_fact_check_action(self, ne_adapter):
        actions = ne_adapter.available_actions()
        names = [a["name"] for a in actions]
        assert "fact_check" in names

    def test_reveal_source_action(self, ne_adapter):
        actions = ne_adapter.available_actions()
        names = [a["name"] for a in actions]
        assert "reveal_source" in names

    def test_respond_to_pressure_action(self, ne_adapter):
        actions = ne_adapter.available_actions()
        names = [a["name"] for a in actions]
        assert "respond_to_pressure" in names


# ── Take Action ────────────────────────────────────────────────────────

class TestTakeAction:

    def test_advance_hour(self, ne_adapter):
        result = ne_adapter.take_action("advance_hour")
        assert "hour" in result

    def test_publish_story(self, ne_adapter):
        result = ne_adapter.take_action("publish_story", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_assign_story(self, ne_adapter):
        result = ne_adapter.take_action(
            "assign_story", reporter_id="rep_chen_li", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_kill_story(self, ne_adapter):
        result = ne_adapter.take_action("kill_story", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_fact_check(self, ne_adapter):
        result = ne_adapter.take_action("fact_check", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_verify_source(self, ne_adapter):
        result = ne_adapter.take_action("verify_source", source_id="src_whistleblower")
        assert result.get("success") is True

    def test_protect_source(self, ne_adapter):
        result = ne_adapter.take_action("protect_source", source_id="src_whistleblower")
        assert result.get("success") is True

    def test_reveal_source(self, ne_adapter):
        result = ne_adapter.take_action("reveal_source", source_id="src_whistleblower")
        assert result.get("success") is True

    def test_sensationalize(self, ne_adapter):
        result = ne_adapter.take_action("sensationalize", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_interview_source(self, ne_adapter):
        result = ne_adapter.take_action("interview_source",
                                        source_id="src_anonymous_tipster")
        assert result.get("success") is True

    def test_staff_break(self, ne_adapter):
        result = ne_adapter.take_action("staff_break",
                                        reporter_id="rep_chen_li", hours=4)
        assert result.get("success") is True

    def test_push_deadline(self, ne_adapter):
        result = ne_adapter.take_action("push_deadline", reporter_id="rep_chen_li")
        assert result.get("success") is True

    def test_editorial_meeting(self, ne_adapter):
        result = ne_adapter.take_action("editorial_meeting")
        assert result.get("success") is True

    def test_do_nothing(self, ne_adapter):
        result = ne_adapter.take_action("do_nothing")
        assert "message" in result

    def test_public_statement(self, ne_adapter):
        result = ne_adapter.take_action("public_statement",
                                        message="We stand firm", honest=True)
        assert result.get("success") is True

    def test_unknown_action(self, ne_adapter):
        result = ne_adapter.take_action("nonexistent_action")
        assert "error" in result

    def test_respond_to_pressure(self, ne_adapter):
        for _ in range(12):
            ne_adapter.take_action("advance_hour")
        result = ne_adapter.take_action("respond_to_pressure",
                                        pressure_id="pressure_advertiser_apex",
                                        action="resist")
        assert result.get("success") is True

    def test_respond_to_legal(self, ne_adapter):
        for _ in range(24):
            ne_adapter.take_action("advance_hour")
        result = ne_adapter.take_action("respond_to_legal",
                                        threat_id="pressure_legal_threat",
                                        action="fight")
        assert result.get("success") is True

    def test_accept_deal(self, ne_adapter):
        for _ in range(8):
            ne_adapter.take_action("advance_hour")
        result = ne_adapter.take_action("accept_deal", deal_id="dilemma_access_deal")
        assert result.get("success") is True

    def test_reject_deal(self, ne_adapter):
        for _ in range(8):
            ne_adapter.take_action("advance_hour")
        result = ne_adapter.take_action("reject_deal", deal_id="dilemma_access_deal")
        assert result.get("success") is True

    def test_retract_story(self, ne_adapter):
        ne_adapter.take_action("publish_story", story_id="story_main_scandal")
        result = ne_adapter.take_action("retract_story", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_update_story(self, ne_adapter):
        ne_adapter.take_action("publish_story", story_id="story_main_scandal")
        result = ne_adapter.take_action("update_story", story_id="story_main_scandal")
        assert result.get("success") is True

    def test_issue_correction(self, ne_adapter):
        ne_adapter.take_action("publish_story", story_id="story_main_scandal")
        result = ne_adapter.take_action("issue_correction",
                                        story_id="story_main_scandal",
                                        details="Fixed headline")
        assert result.get("success") is True


# ── Scoring ────────────────────────────────────────────────────────────

class TestScoring:

    def test_get_score(self, ne_adapter):
        score = ne_adapter.get_score()
        assert "composite" in score
        assert "dimensions" in score

    def test_get_full_score(self, ne_adapter):
        full = ne_adapter.get_full_score()
        assert "composite" in full
        assert "dimensions" in full
        assert "decision_log" in full


# ── Completion ─────────────────────────────────────────────────────────

class TestCompletion:

    def test_not_complete_initially(self, ne_adapter):
        assert ne_adapter.is_complete() is False

    def test_complete_after_all_hours(self, ne_adapter):
        for _ in range(48):
            ne_adapter.take_action("advance_hour")
        assert ne_adapter.is_complete() is True


# ── Decision Log ───────────────────────────────────────────────────────

class TestDecisionLog:

    def test_log_starts_empty(self, ne_adapter):
        assert len(ne_adapter.get_decision_log()) == 0

    def test_log_grows_with_actions(self, ne_adapter):
        ne_adapter.take_action("advance_hour")
        assert len(ne_adapter.get_decision_log()) > 0


# ── Metadata ───────────────────────────────────────────────────────────

class TestMetadata:

    def test_has_name(self, ne_adapter):
        meta = ne_adapter.get_metadata()
        assert meta["name"] == "news_editor"

    def test_has_display_name(self, ne_adapter):
        meta = ne_adapter.get_metadata()
        assert "display_name" in meta

    def test_has_description(self, ne_adapter):
        meta = ne_adapter.get_metadata()
        assert "description" in meta

    def test_has_scoring_axes(self, ne_adapter):
        meta = ne_adapter.get_metadata()
        assert "scoring_axes" in meta
        assert len(meta["scoring_axes"]) == 5
