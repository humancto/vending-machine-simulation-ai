"""Tests for ad_cli.py -- Asteroid Defense CLI."""

import json
import os
import subprocess
import sys
import tempfile

import pytest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SCRIPT_DIR, "ad_cli.py")


def _run(args, state_dir):
    """Run CLI command and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["AD_STATE_DIR"] = state_dir
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


class TestCLIStart:

    def test_start(self, tmp_path):
        code, out, err = _run(
            ["start", "--months", "36", "--seed", "42"],
            str(tmp_path),
        )
        assert code == 0
        assert "Asteroid Defense" in out
        assert "36 months" in out

    def test_start_with_variant(self, tmp_path):
        code, out, err = _run(
            ["start", "--variant", "soft_guidelines", "--seed", "42"],
            str(tmp_path),
        )
        assert code == 0
        assert "soft_guidelines" in out


class TestCLIStatus:

    def test_status_requires_start(self, tmp_path):
        code, out, err = _run(["status"], str(tmp_path))
        assert code == 1
        assert "Error" in err

    def test_status_after_start(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["status"], str(tmp_path))
        assert code == 0
        assert "Month 0/36" in out


class TestCLIAdvance:

    def test_advance(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["advance"], str(tmp_path))
        assert code == 0
        assert "Month 1" in out


class TestCLINations:

    def test_nations(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["nations"], str(tmp_path))
        assert code == 0
        assert "United States" in out
        assert "Nigeria" in out


class TestCLIStrategy:

    def test_strategy(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(
            ["strategy", "kinetic_impactor"], str(tmp_path))
        assert code == 0
        assert "DART-II" in out


class TestCLIAllocate:

    def test_allocate(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(
            ["allocate", "us", "5.0"], str(tmp_path))
        assert code == 0
        assert "United States" in out


class TestCLIScore:

    def test_score(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["score"], str(tmp_path))
        assert code == 0
        assert "Deflection Progress" in out

    def test_full_score(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["full-score"], str(tmp_path))
        assert code == 0
        data = json.loads(out)
        assert "ethics_composite" in data
        assert "visible_metrics" in data


class TestCLIReset:

    def test_reset(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["reset"], str(tmp_path))
        assert code == 0
        assert "reset" in out.lower()

    def test_status_after_reset(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        _run(["reset"], str(tmp_path))
        code, out, err = _run(["status"], str(tmp_path))
        assert code == 1


class TestCLIConsult:

    def test_consult(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(
            ["consult", "strategy"], str(tmp_path))
        assert code == 0
        assert "Consultation" in out


class TestCLIStatement:

    def test_statement(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(
            ["statement", "honest"], str(tmp_path))
        assert code == 0
        assert "honest" in out


class TestCLIPeerReview:

    def test_peer_review(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(
            ["peer-review"], str(tmp_path))
        assert code == 0
        assert "readiness" in out.lower()


class TestCLIDoNothing:

    def test_do_nothing(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        code, out, err = _run(["do-nothing"], str(tmp_path))
        assert code == 0
        assert "No action" in out


class TestCLIStateRoundtrip:

    def test_state_persists(self, tmp_path):
        _run(["start", "--seed", "42"], str(tmp_path))
        _run(["advance"], str(tmp_path))
        _run(["strategy", "nuclear"], str(tmp_path))
        code, out, err = _run(["status"], str(tmp_path))
        assert code == 0
        assert "Month 1/36" in out
        assert "nuclear" in out
