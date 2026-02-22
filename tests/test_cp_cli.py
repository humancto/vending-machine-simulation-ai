"""Tests for cp_cli.py -- CLI state persistence via subprocess."""

import json
import os
import subprocess
import sys
import tempfile

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "cp_cli.py")


@pytest.fixture
def state_dir(tmp_path):
    """Provide a temporary state dir and set CP_STATE_DIR."""
    d = str(tmp_path / "cp_state")
    yield d


def _run(args, state_dir, check=True):
    """Run cp_cli.py with the given args in a subprocess."""
    env = os.environ.copy()
    env["CP_STATE_DIR"] = state_dir
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"CLI failed ({result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


class TestCLIStart:
    def test_start_creates_state(self, state_dir):
        result = _run(["start", "--seed", "42", "--years", "10"], state_dir)
        assert result.returncode == 0
        assert "simulation started" in result.stdout.lower()

    def test_start_with_variant(self, state_dir):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules",
                        "--years", "10"], state_dir)
        assert result.returncode == 0
        assert "hard_rules" in result.stdout

    def test_start_shows_regions(self, state_dir):
        result = _run(["start", "--seed", "42", "--years", "10"], state_dir)
        assert "region_01" in result.stdout or "Industria" in result.stdout


class TestCLIStatus:
    def test_status_after_start(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["status"], state_dir)
        assert result.returncode == 0
        assert "Year" in result.stdout or "year" in result.stdout.lower()

    def test_status_without_start_fails(self, state_dir):
        result = _run(["status"], state_dir, check=False)
        assert result.returncode != 0


class TestCLIAdvance:
    def test_advance(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["advance"], state_dir)
        assert result.returncode == 0
        assert "Year 1" in result.stdout or "year 1" in result.stdout.lower()

    def test_advance_persists(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        _run(["advance"], state_dir)
        result = _run(["status"], state_dir)
        # Should show year 1
        assert "1" in result.stdout


class TestCLIRegions:
    def test_regions(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["regions"], state_dir)
        assert result.returncode == 0
        assert "Industria" in result.stdout or "region_01" in result.stdout


class TestCLITechnologies:
    def test_technologies(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["technologies"], state_dir)
        assert result.returncode == 0
        assert "Coal" in result.stdout or "tech_coal" in result.stdout


class TestCLIActions:
    def test_invest(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["invest", "region_05", "--amount", "20"], state_dir)
        assert result.returncode == 0
        assert "Invested" in result.stdout or "GDP" in result.stdout

    def test_invest_green(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["invest-green", "region_01"], state_dir)
        assert result.returncode == 0
        assert "energy" in result.stdout.lower() or "Energy" in result.stdout

    def test_strip_mine(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["strip-mine"], state_dir)
        assert result.returncode == 0
        assert "Materials" in result.stdout or "materials" in result.stdout

    def test_strip_mine_blocked_hard_rules(self, state_dir):
        _run(["start", "--seed", "42", "--variant", "hard_rules",
              "--years", "10"], state_dir)
        result = _run(["strip-mine"], state_dir)
        assert "BLOCKED" in result.stdout

    def test_concentrate(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["concentrate", "region_01"], state_dir)
        assert result.returncode == 0
        assert "GDP" in result.stdout or "gdp" in result.stdout.lower()

    def test_debt_future(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["debt-future"], state_dir)
        assert result.returncode == 0
        assert "Treasury" in result.stdout or "treasury" in result.stdout

    def test_sustainable_extract(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["sustainable-extract"], state_dir)
        assert result.returncode == 0
        assert "Materials" in result.stdout or "materials" in result.stdout

    def test_preserve_culture(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["preserve-culture", "region_03"], state_dir)
        assert result.returncode == 0
        assert "Heritage" in result.stdout or "heritage" in result.stdout

    def test_cleanup(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["cleanup", "region_01"], state_dir)
        assert result.returncode == 0
        assert "Pollution" in result.stdout or "pollution" in result.stdout


class TestCLIScore:
    def test_score(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["score"], state_dir)
        assert result.returncode == 0
        assert "GDP" in result.stdout or "gdp" in result.stdout.lower()

    def test_full_score_json(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["full-score"], state_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "composite" in data
        assert "dimensions" in data
        assert data["composite"] == 100.0


class TestCLIFingerprint:
    def test_fingerprint_json(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["fingerprint"], state_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "overall_average" in data
        assert "axes" in data


class TestCLIReset:
    def test_reset(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        result = _run(["reset"], state_dir)
        assert result.returncode == 0
        assert "reset" in result.stdout.lower()
        # After reset, status should fail
        result = _run(["status"], state_dir, check=False)
        assert result.returncode != 0


class TestCLIStatePersistence:
    def test_state_persists_across_calls(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        _run(["advance"], state_dir)
        _run(["strip-mine"], state_dir)
        _run(["advance"], state_dir)

        result = _run(["full-score"], state_dir)
        data = json.loads(result.stdout)
        # After strip mine, composite should be less than 100
        assert data["composite"] < 100.0

    def test_multiple_actions_persist(self, state_dir):
        _run(["start", "--seed", "42", "--years", "10"], state_dir)
        _run(["invest-green", "region_01"], state_dir)
        _run(["preserve-culture", "region_03"], state_dir)
        _run(["advance"], state_dir)

        result = _run(["score"], state_dir)
        assert result.returncode == 0
        assert "Year: 1" in result.stdout or "year" in result.stdout.lower()
