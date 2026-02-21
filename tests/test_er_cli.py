"""Tests for er_cli.py — CLI integration tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "er_cli.py")


def _run(args, tmp_path, check=True):
    """Run an er_cli.py command with ER_STATE_DIR pointed at tmp_path."""
    env = os.environ.copy()
    env["ER_STATE_DIR"] = str(tmp_path)
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"CLI failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


class TestStateSaveLoad:

    def test_save_creates_file(self, tmp_path):
        _run(["start", "--seed", "42", "--hours", "72"], tmp_path)
        state_file = tmp_path / "er_sim_state.json"
        assert state_file.exists()

    def test_save_load_roundtrip(self, tmp_path):
        _run(["start", "--seed", "42", "--hours", "72"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Hour 1/72" in result.stdout

    def test_state_file_is_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "er_sim_state.json"
        with open(state_file) as f:
            data = json.load(f)
        assert "current_hour" in data
        assert "patients" in data


class TestCLIStart:

    def test_start_output(self, tmp_path):
        result = _run(["start", "--seed", "42", "--hours", "72"], tmp_path)
        assert "Emergency Room Commander started" in result.stdout
        assert "72 hours" in result.stdout

    def test_start_with_variant(self, tmp_path):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        assert "hard_rules" in result.stdout


class TestCLIStatus:

    def test_status_shows_hour(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Hour 0/72" in result.stdout

    def test_status_shows_resources(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Beds:" in result.stdout
        assert "Surgeons:" in result.stdout


class TestCLIAdvance:

    def test_advance_increments_hour(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Hour 1:" in result.stdout

    def test_advance_twice(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Hour 2:" in result.stdout


class TestCLIWaiting:

    def test_waiting_shows_patients(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["waiting"], tmp_path)
        assert "Waiting Patients" in result.stdout
        assert "Triage:" in result.stdout


class TestCLIFullScore:

    def test_full_score_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["full-score"], tmp_path)
        data = json.loads(result.stdout)
        assert "composite_score" in data
        assert "dimension_scores" in data


class TestCLINoSim:

    def test_status_without_start(self, tmp_path):
        result = _run(["status"], tmp_path, check=False)
        assert result.returncode != 0
        assert "No simulation started" in result.stderr


class TestCLIReset:

    def test_reset_removes_state(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "er_sim_state.json"
        assert state_file.exists()
        _run(["reset"], tmp_path)
        assert not state_file.exists()
