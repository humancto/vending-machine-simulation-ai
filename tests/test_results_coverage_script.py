"""Tests for scripts/results_coverage.py."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from race.scenario_registry import scenario_ids


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "results_coverage.py"


def run_coverage(args):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout, completed.stderr


def test_results_coverage_reports_known_and_unknown_records():
    with tempfile.TemporaryDirectory(dir=ROOT / "results", prefix="coverage_test_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        results_file = tmp_path / "sample.json"
        results_file.write_text(
            json.dumps(
                [
                    {
                        "simulation": "prisoners_dilemma",
                        "variant": "hard_rules",
                        "seed": 11,
                        "results": [
                            {"agent": "codex", "agent_type": "codex", "composite_score": 51.0}
                        ],
                    },
                    {
                        "simulation": "unknown_sim",
                        "variant": "soft_guidelines",
                        "seed": 12,
                        "results": [{"agent": "claude", "agent_type": "claude"}],
                    },
                ]
            ),
            encoding="utf-8",
        )

        rel_glob = f"{tmp_path.relative_to(ROOT)}/**/*.json"
        code, stdout, stderr = run_coverage(["--results-glob", rel_glob, "--print-json", "--quiet"])
        assert code == 0, stderr

    payload = json.loads(stdout)
    assert payload["schema_version"] == "results_coverage_v1"
    assert payload["simulations_total"] == len(scenario_ids())
    assert payload["simulations_with_results"] == 1
    assert payload["unknown_simulation_records"]["unknown_sim"] == 1

    row = next(r for r in payload["per_simulation"] if r["simulation"] == "prisoners_dilemma")
    assert row["record_count"] == 1
    assert row["seed_count"] == 1
    assert row["variants"] == ["hard_rules"]
    assert row["agent_counts"]["codex"] == 1


def test_results_coverage_threshold_and_output_file(tmp_path):
    with tempfile.TemporaryDirectory(dir=ROOT / "results", prefix="coverage_test_") as tmp_dir:
        tmp_results = Path(tmp_dir)
        (tmp_results / "sample.json").write_text(
            json.dumps(
                [
                    {
                        "simulation": "vending_machine",
                        "variant": "soft_guidelines",
                        "seed": 22,
                        "results": [{"agent": "codex", "agent_type": "codex"}],
                    }
                ]
            ),
            encoding="utf-8",
        )
        rel_glob = f"{tmp_results.relative_to(ROOT)}/**/*.json"
        output_file = tmp_path / "coverage.json"

        code_fail, stdout_fail, stderr_fail = run_coverage(
            [
                "--results-glob",
                rel_glob,
                "--output",
                str(output_file),
                "--quiet",
                "--min-simulations-with-results",
                "2",
            ]
        )
        assert code_fail == 1, stderr_fail
        assert "Coverage summary saved to" in stdout_fail
        assert output_file.exists()

        code_pass, _, stderr_pass = run_coverage(
            [
                "--results-glob",
                rel_glob,
                "--quiet",
                "--min-simulations-with-results",
                "1",
            ]
        )
        assert code_pass == 0, stderr_pass
