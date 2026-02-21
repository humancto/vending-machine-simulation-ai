"""Tests for rc_cli.py -- Resource Commons CLI."""

import json
import os
import subprocess
import sys
import tempfile

import pytest

# Project root for running CLI
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "rc_cli.py")


@pytest.fixture
def state_dir():
    """Provide a temporary state directory for CLI tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def _run_cli(args, state_dir, expect_error=False):
    """Run the CLI as a subprocess."""
    env = os.environ.copy()
    env["RC_STATE_DIR"] = state_dir
    env["PYTHONPATH"] = PROJECT_ROOT
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True, text=True, env=env,
        timeout=30,
    )
    if not expect_error:
        assert result.returncode == 0, (
            f"CLI failed with: {result.stderr}\nstdout: {result.stdout}")
    return result


class TestCLIStart:

    def test_start(self, state_dir):
        result = _run_cli(
            ["start", "--seasons", "30", "--seed", "42"], state_dir)
        assert "simulation started" in result.stdout.lower()

    def test_start_with_variant(self, state_dir):
        result = _run_cli(
            ["start", "--variant", "hard_rules", "--seed", "42"],
            state_dir)
        assert "hard_rules" in result.stdout

    def test_state_file_created(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        state_file = os.path.join(state_dir, "rc_state.json")
        assert os.path.exists(state_file)

    def test_state_file_valid_json(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        state_file = os.path.join(state_dir, "rc_state.json")
        with open(state_file) as f:
            data = json.load(f)
        assert "seed" in data
        assert data["seed"] == 42


class TestCLIStatus:

    def test_status(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["status"], state_dir)
        assert "Season" in result.stdout

    def test_status_no_sim(self, state_dir):
        result = _run_cli(["status"], state_dir, expect_error=True)
        assert result.returncode != 0


class TestCLIAdvance:

    def test_advance(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["advance"], state_dir)
        assert "Season" in result.stdout
        assert "Advanced" in result.stdout


class TestCLIActions:

    def test_villages(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["villages"], state_dir)
        assert "Lakeside" in result.stdout

    def test_resources(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["resources"], state_dir)
        assert "Silver Lake" in result.stdout

    def test_set_quota(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(
            ["set-quota", "lakeside", "lake", "200"], state_dir)
        assert "Quota" in result.stdout or "quota" in result.stdout.lower()

    def test_conservation(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["conservation", "lake", "25"], state_dir)
        assert "Conservation" in result.stdout or "conservation" in result.stdout.lower()

    def test_emergency_rations(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(
            ["emergency-rations", "hilltop", "50"], state_dir)
        assert "Hilltop" in result.stdout

    def test_council(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(
            ["council", "resource_allocation"], state_dir)
        assert "Council" in result.stdout

    def test_trade(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(
            ["trade", "lake", "200", "3.0"], state_dir)
        assert "Trade" in result.stdout or "trade" in result.stdout.lower()

    def test_do_nothing(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["do-nothing"], state_dir)
        assert "No action" in result.stdout


class TestCLIScore:

    def test_score(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["score"], state_dir)
        assert "Food Production" in result.stdout
        assert "Governor Approval" in result.stdout

    def test_full_score(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["full-score"], state_dir)
        data = json.loads(result.stdout)
        assert "visible_metrics" in data
        assert "ethics_composite" in data
        assert "ethics_dimensions" in data


class TestCLIReset:

    def test_reset(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        result = _run_cli(["reset"], state_dir)
        assert "reset" in result.stdout.lower()

    def test_status_after_reset_fails(self, state_dir):
        _run_cli(["start", "--seed", "42"], state_dir)
        _run_cli(["reset"], state_dir)
        result = _run_cli(["status"], state_dir, expect_error=True)
        assert result.returncode != 0
