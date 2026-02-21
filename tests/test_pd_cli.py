"""Tests for pd_cli.py — Prisoner's Dilemma CLI interface."""

import json
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestStatePersistence:

    def test_save_load_roundtrip(self, tmp_path):
        import pd_cli
        from simulations.prisoners_dilemma.simulation import PrisonersDilemmaSim

        original_file = pd_cli.STATE_FILE
        pd_cli.STATE_FILE = str(tmp_path / "test_state.json")
        try:
            sim = PrisonersDilemmaSim(seed=42, total_rounds=10)
            sim.make_move("C")
            sim.make_move("D")
            pd_cli._save_sim(sim)

            loaded = pd_cli._load_sim()
            assert loaded is not None
            assert loaded.current_round == sim.current_round
            assert loaded.player_total_score == sim.player_total_score
            assert loaded._cooperate_count == sim._cooperate_count
            assert loaded._defect_count == sim._defect_count
        finally:
            pd_cli.STATE_FILE = original_file

    def test_load_nonexistent(self, tmp_path):
        import pd_cli

        original_file = pd_cli.STATE_FILE
        pd_cli.STATE_FILE = str(tmp_path / "nonexistent.json")
        try:
            assert pd_cli._load_sim() is None
        finally:
            pd_cli.STATE_FILE = original_file

    def test_save_preserves_opponent_state(self, tmp_path):
        import pd_cli
        from simulations.prisoners_dilemma.simulation import PrisonersDilemmaSim

        original_file = pd_cli.STATE_FILE
        pd_cli.STATE_FILE = str(tmp_path / "test_state.json")
        try:
            sim = PrisonersDilemmaSim(seed=42, total_rounds=10, num_opponents=3)
            for _ in range(6):
                sim.make_move("C")
            pd_cli._save_sim(sim)

            loaded = pd_cli._load_sim()
            for i in range(3):
                assert len(loaded.opponents[i].history) == len(sim.opponents[i].history)
                assert len(loaded.opponents[i].player_history) == len(sim.opponents[i].player_history)
        finally:
            pd_cli.STATE_FILE = original_file


class TestCLISubprocess:

    def test_start_creates_state(self, tmp_path):
        env = {**os.environ, "PD_STATE_DIR": str(tmp_path)}
        result = subprocess.run(
            [sys.executable, "pd_cli.py", "start", "--rounds", "5", "--seed", "42"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0
        assert os.path.exists(tmp_path / "pd_sim_state.json")
        assert "started" in result.stdout.lower()

    def test_move_advances_game(self, tmp_path):
        env = {**os.environ, "PD_STATE_DIR": str(tmp_path)}
        subprocess.run(
            [sys.executable, "pd_cli.py", "start", "--rounds", "5", "--seed", "42"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        result = subprocess.run(
            [sys.executable, "pd_cli.py", "move", "C"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0
        assert "Round" in result.stdout

    def test_full_score_outputs_json(self, tmp_path):
        env = {**os.environ, "PD_STATE_DIR": str(tmp_path)}
        subprocess.run(
            [sys.executable, "pd_cli.py", "start", "--rounds", "5", "--seed", "42"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        for _ in range(5):
            subprocess.run(
                [sys.executable, "pd_cli.py", "move", "C"],
                capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
            )
        result = subprocess.run(
            [sys.executable, "pd_cli.py", "full-score"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0
        score = json.loads(result.stdout)
        assert "composite_score" in score

    def test_status_before_start_fails(self, tmp_path):
        env = {**os.environ, "PD_STATE_DIR": str(tmp_path)}
        result = subprocess.run(
            [sys.executable, "pd_cli.py", "status"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert result.returncode != 0

    def test_reset_clears_state(self, tmp_path):
        env = {**os.environ, "PD_STATE_DIR": str(tmp_path)}
        subprocess.run(
            [sys.executable, "pd_cli.py", "start", "--rounds", "5", "--seed", "42"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert os.path.exists(tmp_path / "pd_sim_state.json")

        result = subprocess.run(
            [sys.executable, "pd_cli.py", "reset"],
            capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0
        assert not os.path.exists(tmp_path / "pd_sim_state.json")
