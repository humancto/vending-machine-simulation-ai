"""Tests for scripts/full_campaign.py."""

import json
import subprocess
import sys
from pathlib import Path

from race.scenario_registry import scenario_ids


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "full_campaign.py"


def run_campaign(args):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout, completed.stderr


def test_full_campaign_dry_run_writes_progress_and_summary(tmp_path):
    results_dir = tmp_path / "campaign"
    code, stdout, stderr = run_campaign(
        [
            "--agents",
            "codex",
            "--variant",
            "soft_guidelines",
            "--limit",
            "2",
            "--results-dir",
            str(results_dir),
            "--dry-run",
        ]
    )
    assert code == 0, stderr
    assert "Campaign summary saved to" in stdout

    progress = json.loads((results_dir / "progress.json").read_text(encoding="utf-8"))
    summary = json.loads((results_dir / "summary.json").read_text(encoding="utf-8"))

    assert progress["schema_version"] == "all_sims_campaign_v1"
    assert summary["schema_version"] == "all_sims_campaign_summary_v1"
    assert len(progress["runs"]) == 2
    assert summary["runs_total"] == 2
    assert summary["runs_ok"] == 2
    assert summary["runs_failed"] == 0
    assert not (results_dir / "coverage.json").exists()
    assert not (results_dir / "quality_report.json").exists()


def test_full_campaign_resume_skips_successful_runs(tmp_path):
    results_dir = tmp_path / "campaign"
    code_1, _, stderr_1 = run_campaign(
        [
            "--agents",
            "codex",
            "--variant",
            "soft_guidelines",
            "--limit",
            "1",
            "--results-dir",
            str(results_dir),
            "--dry-run",
        ]
    )
    assert code_1 == 0, stderr_1

    code_2, _, stderr_2 = run_campaign(
        [
            "--agents",
            "codex",
            "--variant",
            "soft_guidelines",
            "--limit",
            "2",
            "--results-dir",
            str(results_dir),
            "--dry-run",
        ]
    )
    assert code_2 == 0, stderr_2

    progress = json.loads((results_dir / "progress.json").read_text(encoding="utf-8"))
    runs = progress["runs"]
    assert len(runs) == 2
    assert runs[0]["simulation"] != runs[1]["simulation"]


def test_full_campaign_dry_run_uses_sorted_registry_order(tmp_path):
    results_dir = tmp_path / "campaign"
    code, _, stderr = run_campaign(
        [
            "--agents",
            "codex",
            "--variant",
            "hard_rules",
            "--limit",
            "3",
            "--results-dir",
            str(results_dir),
            "--dry-run",
        ]
    )
    assert code == 0, stderr

    progress = json.loads((results_dir / "progress.json").read_text(encoding="utf-8"))
    actual = [row["simulation"] for row in progress["runs"]]
    expected = sorted(scenario_ids())[:3]
    assert actual == expected
