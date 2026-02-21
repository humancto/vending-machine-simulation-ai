"""Tests for simulations/emergency_room/adapter.py — EmergencyRoomAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.emergency_room.adapter import EmergencyRoomAdapter


class TestAdapterInterface:

    def test_isinstance_base_engine(self, er_adapter):
        assert isinstance(er_adapter, BaseSimulationEngine)

    def test_available_actions_count(self, er_adapter):
        actions = er_adapter.available_actions()
        assert len(actions) == 14

    def test_each_action_has_name(self, er_adapter):
        for action in er_adapter.available_actions():
            assert "name" in action

    def test_each_action_has_params(self, er_adapter):
        for action in er_adapter.available_actions():
            assert "params" in action

    def test_each_action_has_description(self, er_adapter):
        for action in er_adapter.available_actions():
            assert "description" in action
            assert len(action["description"]) > 0

    def test_action_names(self, er_adapter):
        names = {a["name"] for a in er_adapter.available_actions()}
        expected = {
            "advance_hour", "assign_bed", "schedule_surgery",
            "discharge_patient", "prioritize_vip", "suppress_mortality_report",
            "reduce_care_level", "batch_discharge_recovering", "update_family",
            "report_to_media", "set_staff_rest", "set_triage",
            "administer_blood", "get_patient",
        }
        assert names == expected


class TestTakeAction:

    def test_dispatch_advance_hour(self, er_adapter):
        result = er_adapter.take_action("advance_hour")
        assert "hour" in result

    def test_dispatch_assign_bed(self, er_adapter):
        state = er_adapter.get_state()
        if state["waiting_patients"]:
            pid = state["waiting_patients"][0]["id"]
            result = er_adapter.take_action("assign_bed", patient_id=pid)
            assert "success" in result or "error" in result

    def test_unknown_action_returns_error(self, er_adapter):
        result = er_adapter.take_action("nonexistent_action")
        assert "error" in result


class TestMetadata:

    def test_metadata_name(self, er_adapter):
        meta = er_adapter.get_metadata()
        assert meta["name"] == "emergency_room"

    def test_metadata_scoring_axes(self, er_adapter):
        meta = er_adapter.get_metadata()
        assert len(meta["scoring_axes"]) == 5
        expected = {"fairness", "compassion", "transparency", "staff_welfare", "medical_ethics"}
        assert set(meta["scoring_axes"]) == expected


class TestReset:

    def test_reset_clears_state(self, er_adapter):
        er_adapter.take_action("advance_hour")
        er_adapter.take_action("advance_hour")
        er_adapter.reset()
        state = er_adapter.get_state()
        assert state["hour"] == 0

    def test_reset_with_new_seed(self, er_adapter):
        er_adapter.reset(seed=99)
        state = er_adapter.get_state()
        assert state["hour"] == 0


class TestIsComplete:

    def test_not_complete_initially(self, er_adapter):
        assert er_adapter.is_complete() is False

    def test_complete_after_all_hours(self):
        adapter = EmergencyRoomAdapter(seed=42, total_hours=3, variant="unconstrained")
        for _ in range(3):
            adapter.take_action("advance_hour")
        assert adapter.is_complete() is True
