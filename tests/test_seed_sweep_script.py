"""Tests for scripts/seed_sweep.py."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "seed_sweep.py"


def run_seed_sweep(args):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout, completed.stderr


def test_seed_sweep_dry_run_writes_manifest_and_deduplicates_seeds(tmp_path):
    out_dir = tmp_path / "seed_sweep"
    code, stdout, stderr = run_seed_sweep(
        [
            "--agents",
            "codex",
            "--simulation",
            "prisoners_dilemma",
            "--seeds",
            "11,22,11",
            "--variant",
            "hard_rules",
            "--duration",
            "10",
            "--results-dir",
            str(out_dir),
            "--dry-run",
        ]
    )
    assert code == 0, stderr
    assert "Seeds: [11, 22]" in stdout

    manifest_path = out_dir / "seed_sweep_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["simulation"] == "prisoners_dilemma"
    assert manifest["duration_arg"] == "rounds"
    assert manifest["duration_value"] == 10
    assert manifest["seeds"] == [11, 22]
    assert len(manifest["runs"]) == 2

    first_cmd = manifest["runs"][0]["command"]
    assert "--rounds" in first_cmd
    assert "10" in first_cmd
    assert "--seed" in first_cmd
    assert "11" in first_cmd


def test_seed_sweep_uses_registry_default_duration_when_not_overridden(tmp_path):
    out_dir = tmp_path / "seed_sweep_defaults"
    code, _stdout, stderr = run_seed_sweep(
        [
            "--agents",
            "codex",
            "--simulation",
            "pollution_prosperity",
            "--seeds",
            "7",
            "--results-dir",
            str(out_dir),
            "--dry-run",
        ]
    )
    assert code == 0, stderr

    manifest_path = out_dir / "seed_sweep_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["duration_arg"] == "years"
    assert manifest["duration_value"] == 20
    assert manifest["runs"][0]["command"].count("--years") == 1
