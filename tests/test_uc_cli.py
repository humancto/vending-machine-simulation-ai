"""Tests for uc_cli.py -- CLI state persistence via subprocess."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

# Project root for running CLI
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "uc_cli.py")


@pytest.fixture
def tmp_state_dir():
    """Create a temporary state directory for CLI tests."""
    d = tempfile.mkdtemp(prefix="uc_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _run(args, state_dir):
    """Run the CLI with a custom state dir."""
    env = os.environ.copy()
    env["UC_STATE_DIR"] = state_dir
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True, text=True, env=env,
        cwd=PROJECT_ROOT,
    )
    return result


class TestCLIStart:
    def test_start_creates_state(self, tmp_state_dir):
        r = _run(["start", "--seed", "42", "--days", "10"], tmp_state_dir)
        assert r.returncode == 0
        assert "simulation started" in r.stdout.lower()
        state_file = os.path.join(tmp_state_dir, "uc_state.json")
        assert os.path.exists(state_file)

    def test_start_with_variant(self, tmp_state_dir):
        r = _run(["start", "--variant", "hard_rules"], tmp_state_dir)
        assert r.returncode == 0
        assert "hard_rules" in r.stdout

    def test_start_shows_crises(self, tmp_state_dir):
        r = _run(["start", "--seed", "42"], tmp_state_dir)
        assert "crisis" in r.stdout.lower()


class TestCLIStatus:
    def test_status_requires_start(self, tmp_state_dir):
        r = _run(["status"], tmp_state_dir)
        assert r.returncode != 0

    def test_status_after_start(self, tmp_state_dir):
        _run(["start", "--seed", "42", "--days", "10"], tmp_state_dir)
        r = _run(["status"], tmp_state_dir)
        assert r.returncode == 0
        assert "Day" in r.stdout


class TestCLIAdvance:
    def test_advance(self, tmp_state_dir):
        _run(["start", "--seed", "42", "--days", "10"], tmp_state_dir)
        r = _run(["advance"], tmp_state_dir)
        assert r.returncode == 0
        assert "Day 1" in r.stdout

    def test_advance_persists(self, tmp_state_dir):
        _run(["start", "--seed", "42", "--days", "10"], tmp_state_dir)
        _run(["advance"], tmp_state_dir)
        r = _run(["status"], tmp_state_dir)
        assert "Day" in r.stdout


class TestCLICrises:
    def test_crises_command(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["crises"], tmp_state_dir)
        assert r.returncode == 0
        assert "crisis" in r.stdout.lower()


class TestCLIRegions:
    def test_regions_command(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["regions"], tmp_state_dir)
        assert r.returncode == 0
        assert "region" in r.stdout.lower()


class TestCLIDonors:
    def test_donors_command(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["donors"], tmp_state_dir)
        assert r.returncode == 0
        assert "donor" in r.stdout.lower()


class TestCLIAllocate:
    def test_allocate(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["allocate", "crisis_01", "--money", "10",
                  "--personnel", "50"], tmp_state_dir)
        assert r.returncode == 0
        assert "allocated" in r.stdout.lower()


class TestCLIScore:
    def test_score(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["score"], tmp_state_dir)
        assert r.returncode == 0
        assert "Reputation" in r.stdout

    def test_full_score(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["full-score"], tmp_state_dir)
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "composite" in data
        assert "dimensions" in data


class TestCLIReset:
    def test_reset(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["reset"], tmp_state_dir)
        assert r.returncode == 0
        assert "reset" in r.stdout.lower()
        # After reset, status should fail
        r2 = _run(["status"], tmp_state_dir)
        assert r2.returncode != 0


class TestCLITemptations:
    def test_suppress_failure(self, tmp_state_dir):
        _run(["start", "--seed", "42", "--variant", "unconstrained"], tmp_state_dir)
        r = _run(["suppress-failure"], tmp_state_dir)
        assert r.returncode == 0
        assert "suppressed" in r.stdout.lower()

    def test_suppress_failure_blocked_hard(self, tmp_state_dir):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_state_dir)
        r = _run(["suppress-failure"], tmp_state_dir)
        assert r.returncode == 0
        assert "BLOCKED" in r.stdout

    def test_bypass_local(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["bypass-local", "region_05"], tmp_state_dir)
        assert r.returncode == 0
        assert "bypass" in r.stdout.lower() or "Efficiency" in r.stdout


class TestCLIEthical:
    def test_empower_local(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["empower-local", "region_05"], tmp_state_dir)
        assert r.returncode == 0
        assert "empower" in r.stdout.lower() or "Local" in r.stdout

    def test_transparent_report(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["transparent-report"], tmp_state_dir)
        assert r.returncode == 0
        assert "report" in r.stdout.lower()


class TestCLIFingerprint:
    def test_fingerprint(self, tmp_state_dir):
        _run(["start", "--seed", "42"], tmp_state_dir)
        r = _run(["fingerprint"], tmp_state_dir)
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "overall_average" in data
        assert "axes" in data
        assert len(data["axes"]) == 12
