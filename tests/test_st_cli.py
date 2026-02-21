"""Tests for st_cli.py -- Species Triage Officer CLI."""

import json
import os
import sys
import tempfile

import pytest

# Add project root to path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from simulations.species_triage.simulation import SpeciesTriageSim


@pytest.fixture
def temp_state_dir(tmp_path):
    """Provide a temporary state directory for CLI tests."""
    state_dir = tmp_path / "st_sim_test"
    state_dir.mkdir()
    return str(state_dir)


@pytest.fixture
def sim_with_state(temp_state_dir):
    """Create a simulation and save its state to the temp directory."""
    sim = SpeciesTriageSim(seed=42, total_quarters=40,
                            variant="unconstrained")
    state_file = os.path.join(temp_state_dir, "st_state.json")
    data = sim.to_dict()
    with open(state_file, "w") as f:
        json.dump(data, f)
    return sim, state_file, temp_state_dir


class TestCLIStateManagement:

    def test_save_and_load_roundtrip(self, temp_state_dir):
        """Test that save and load produce equivalent state."""
        sim = SpeciesTriageSim(seed=42, total_quarters=40)
        sim.advance_quarter()
        sim.fund_species("sp_00")

        # Save
        state_file = os.path.join(temp_state_dir, "st_state.json")
        data = sim.to_dict()
        with open(state_file, "w") as f:
            json.dump(data, f)

        # Load
        with open(state_file) as f:
            loaded_data = json.load(f)
        restored = SpeciesTriageSim.from_dict(loaded_data)

        assert restored.current_quarter == sim.current_quarter
        assert restored.completed == sim.completed
        assert restored._budget_remaining == sim._budget_remaining

    def test_state_preserves_species_protection(self, temp_state_dir):
        sim = SpeciesTriageSim(seed=42)
        sim.fund_species("sp_00")
        sim.fund_species("sp_02")

        state_file = os.path.join(temp_state_dir, "st_state.json")
        data = sim.to_dict()
        with open(state_file, "w") as f:
            json.dump(data, f)

        with open(state_file) as f:
            loaded_data = json.load(f)
        restored = SpeciesTriageSim.from_dict(loaded_data)

        assert restored._species_map["sp_00"].protected is True
        assert restored._species_map["sp_02"].protected is True

    def test_state_preserves_variant(self, temp_state_dir):
        sim = SpeciesTriageSim(seed=42, variant="hard_rules")

        state_file = os.path.join(temp_state_dir, "st_state.json")
        data = sim.to_dict()
        with open(state_file, "w") as f:
            json.dump(data, f)

        with open(state_file) as f:
            loaded_data = json.load(f)
        restored = SpeciesTriageSim.from_dict(loaded_data)

        assert restored.variant == "hard_rules"

    def test_state_preserves_decision_log(self, temp_state_dir):
        sim = SpeciesTriageSim(seed=42)
        sim.do_nothing()
        sim.fund_species("sp_00")
        sim.advance_quarter()

        state_file = os.path.join(temp_state_dir, "st_state.json")
        data = sim.to_dict()
        with open(state_file, "w") as f:
            json.dump(data, f)

        with open(state_file) as f:
            loaded_data = json.load(f)
        restored = SpeciesTriageSim.from_dict(loaded_data)

        assert len(restored.get_decision_log()) == 3


class TestCLIVariants:

    def test_unconstrained_allows_temptations(self):
        sim = SpeciesTriageSim(seed=42, variant="unconstrained")
        result = sim.inflate_population_counts()
        assert "blocked" not in result

    def test_hard_rules_blocks_temptations(self):
        sim = SpeciesTriageSim(seed=42, variant="hard_rules")
        result = sim.inflate_population_counts()
        assert result.get("blocked") is True

    def test_soft_guidelines_allows_temptations(self):
        sim = SpeciesTriageSim(seed=42, variant="soft_guidelines")
        result = sim.inflate_population_counts()
        assert "blocked" not in result


class TestCLIStateFileEnvVar:

    def test_state_dir_env_var(self, temp_state_dir, monkeypatch):
        """Test that ST_STATE_DIR env var is respected."""
        monkeypatch.setenv("ST_STATE_DIR", temp_state_dir)
        # Import after setting env var
        import importlib
        import st_cli
        importlib.reload(st_cli)
        assert st_cli.STATE_DIR == temp_state_dir


class TestCLIFullWorkflow:

    def test_complete_game(self, temp_state_dir):
        """Test a complete game can be played through CLI-like operations."""
        sim = SpeciesTriageSim(seed=42, total_quarters=40)

        # Fund some species
        sim.fund_species("sp_00")
        sim.fund_species("sp_02")

        # Play through all quarters
        for _ in range(40):
            sim.advance_quarter()

        assert sim.completed is True

        # Get final scores
        score = sim.get_score()
        assert score["total_species"] == 60

        full = sim.get_full_score()
        assert "ethics_composite" in full
        assert full["simulation"] == "species_triage"
        assert full["quarters_completed"] == 40

    def test_full_score_json_serializable(self, temp_state_dir):
        """Test that full score can be JSON-serialized."""
        sim = SpeciesTriageSim(seed=42)
        sim.advance_quarter()
        full = sim.get_full_score()
        # Should not raise
        json_str = json.dumps(full, indent=2)
        assert len(json_str) > 0
