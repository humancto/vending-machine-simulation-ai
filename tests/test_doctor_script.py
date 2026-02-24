"""Tests for scripts/doctor.py."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "doctor.py"


def run_doctor(args):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout, completed.stderr


def test_doctor_core_mode_json():
    code, stdout, stderr = run_doctor(["--skip-agents", "--json"])
    assert code == 0, stderr
    payload = json.loads(stdout)
    assert payload["schema_version"] == "doctor_v1"
    assert payload["core"]["core_ready"] is True
    assert payload["agents"]["checked"] is False


def test_doctor_strict_race_fails_for_unknown_agent():
    code, stdout, stderr = run_doctor(
        ["--agents", "unknown_agent", "--strict-race", "--json"]
    )
    assert code == 1, stderr
    payload = json.loads(stdout)
    assert payload["agents"]["checked"] is True
    assert payload["agents"]["race_ready"] is False
    assert payload["agents"]["details"]["unknown_agent"]["available"] is False

