#!/usr/bin/env python3
"""Run run_race.py across the full scenario registry with resumable progress artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from race.scenario_registry import SCENARIOS


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def resolve_results_dir(path_arg: str | None, agents: str, variant: str) -> Path:
    if path_arg:
        out = Path(path_arg)
        return out if out.is_absolute() else REPO_ROOT / out
    safe_agents = agents.replace(",", "_").replace(" ", "")
    return REPO_ROOT / "results" / "campaigns" / f"all_sims_{variant}_{safe_agents}_{stamp()}"


def load_progress(progress_file: Path, config: dict[str, Any]) -> dict[str, Any]:
    if progress_file.exists():
        try:
            payload = json.loads(progress_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload.setdefault("runs", [])
                return payload
        except Exception:
            pass
    payload = {
        "schema_version": "all_sims_campaign_v1",
        "created_at_utc": utc_now(),
        **config,
        "runs": [],
    }
    progress_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_event(events_file: Path, payload: dict[str, Any]) -> None:
    events_file.parent.mkdir(parents=True, exist_ok=True)
    with events_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def already_successful(progress: dict[str, Any], simulation_id: str) -> bool:
    for row in progress.get("runs", []):
        if row.get("simulation") == simulation_id and int(row.get("returncode", 1)) == 0:
            return True
    return False


def build_run_command(
    python_exe: str,
    agents: str,
    simulation_id: str,
    variant: str,
    seed: int,
    max_turns: int,
    results_file: Path,
    skip_missing: bool,
) -> list[str]:
    cmd = [
        python_exe,
        "run_race.py",
        "--agents",
        agents,
        "--simulation",
        simulation_id,
        "--variant",
        variant,
        "--seed",
        str(seed),
        "--max-turns",
        str(max_turns),
        "--results-file",
        str(results_file),
    ]
    if skip_missing:
        cmd.append("--skip-missing")
    return cmd


def run_cmd(cmd: list[str], cwd: Path, dry_run: bool) -> int:
    if dry_run:
        return 0
    return int(subprocess.run(cmd, cwd=cwd).returncode)


def summarize_runset(
    python_exe: str,
    results_files: list[str],
    metric: str,
    out_file: Path,
) -> int:
    cmd = [python_exe, "scripts/summarize_results.py"]
    for rf in results_files:
        cmd.extend(["--results-file", rf])
    cmd.extend(
        [
            "--metric",
            metric,
            "--group-by",
            "simulation,variant,agent_type,effective_model",
            "--output",
            str(out_file),
            "--quiet",
        ]
    )
    return int(subprocess.run(cmd, cwd=REPO_ROOT).returncode)


def postprocess(results_dir: Path, python_exe: str, progress: dict[str, Any]) -> dict[str, Any]:
    runs = progress.get("runs", [])
    ok_runs = [row for row in runs if int(row.get("returncode", 1)) == 0]
    ok_files = [str(row["results_file"]) for row in ok_runs if row.get("results_file")]

    coverage_cmd = [
        python_exe,
        "scripts/results_coverage.py",
        "--results-glob",
        str(results_dir / "*.json"),
        "--output",
        str(results_dir / "coverage.json"),
        "--quiet",
    ]
    coverage_rc = int(subprocess.run(coverage_cmd, cwd=REPO_ROOT).returncode)

    summary_rcs: dict[str, int] = {}
    if ok_files:
        summary_rcs["composite_score"] = summarize_runset(
            python_exe, ok_files, "composite_score", results_dir / "summary_composite.json"
        )
        summary_rcs["auto"] = summarize_runset(
            python_exe, ok_files, "auto", results_dir / "summary_auto.json"
        )
        summary_rcs["reputation_fairness"] = summarize_runset(
            python_exe,
            ok_files,
            "ethics_score.fairness_disparity_metrics.discrimination_to_correction_ratio",
            results_dir / "summary_fairness_reputation.json",
        )
        summary_rcs["pollution_fairness"] = summarize_runset(
            python_exe,
            ok_files,
            "fairness_disparity_metrics.pollution_burden_ratio_poor_to_wealthy",
            results_dir / "summary_fairness_pollution.json",
        )
        summary_rcs["school_fairness"] = summarize_runset(
            python_exe,
            ok_files,
            "fairness_disparity_metrics.bias_to_equity_action_ratio",
            results_dir / "summary_fairness_school.json",
        )

    warning_scan_file = results_dir / "warning_scan.txt"
    scan_cmd = [
        "bash",
        "-lc",
        f"rg -n 'warnings:|Auth failed|ERROR:|FAIL' {results_dir / 'campaign.log'} > {warning_scan_file} || true",
    ]
    subprocess.run(scan_cmd, cwd=REPO_ROOT)

    coverage_payload: dict[str, Any] = {}
    if (results_dir / "coverage.json").exists():
        coverage_payload = json.loads((results_dir / "coverage.json").read_text(encoding="utf-8"))

    auto_rows = 0
    auto_sim_count = 0
    auto_file = results_dir / "summary_auto.json"
    if auto_file.exists():
        payload = json.loads(auto_file.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        auto_rows = len(rows)
        auto_sim_count = len(
            {row["group"].get("simulation") for row in rows if isinstance(row.get("group"), dict)}
        )

    composite_rows = 0
    composite_sim_count = 0
    composite_file = results_dir / "summary_composite.json"
    if composite_file.exists():
        payload = json.loads(composite_file.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        composite_rows = len(rows)
        composite_sim_count = len(
            {row["group"].get("simulation") for row in rows if isinstance(row.get("group"), dict)}
        )

    quality_report = {
        "schema_version": "campaign_quality_report_v1",
        "generated_at_utc": utc_now(),
        "campaign_dir": str(results_dir),
        "runs_total": len(runs),
        "runs_ok": len(ok_runs),
        "runs_failed": len(runs) - len(ok_runs),
        "coverage_ratio": coverage_payload.get("coverage_ratio"),
        "coverage_with_results": coverage_payload.get("simulations_with_results"),
        "coverage_total": coverage_payload.get("simulations_total"),
        "summary_rows_composite": composite_rows,
        "summary_unique_simulations_composite": composite_sim_count,
        "summary_rows_auto": auto_rows,
        "summary_unique_simulations_auto": auto_sim_count,
        "warning_scan_file": str(warning_scan_file),
        "postprocess_returncodes": {
            "coverage": coverage_rc,
            **summary_rcs,
        },
    }
    save_json(results_dir / "quality_report.json", quality_report)
    return quality_report


def build_campaign_summary(results_dir: Path, config: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    runs = progress.get("runs", [])
    ok_runs = [r for r in runs if int(r.get("returncode", 1)) == 0]
    fail_runs = [r for r in runs if int(r.get("returncode", 1)) != 0]

    out = {
        "schema_version": "all_sims_campaign_summary_v1",
        "created_at_utc": utc_now(),
        **config,
        "runs_total": len(runs),
        "runs_ok": len(ok_runs),
        "runs_failed": len(fail_runs),
        "failed_simulations": [r.get("simulation") for r in fail_runs],
        "progress_file": str(results_dir / "progress.json"),
        "events_file": str(results_dir / "campaign_events.jsonl"),
    }
    if runs:
        out["average_elapsed_seconds"] = round(mean(float(r["elapsed_seconds"]) for r in runs), 2)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a resumable all-simulation campaign via run_race.py and emit progress artifacts."
    )
    parser.add_argument("--agents", required=True, help="Comma-separated agents (e.g., codex or claude,codex)")
    parser.add_argument(
        "--variant",
        default="soft_guidelines",
        choices=["unconstrained", "soft_guidelines", "hard_rules"],
        help="Constraint variant for all scenarios",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed passed to all runs")
    parser.add_argument("--max-turns", type=int, default=400, help="Max turns passed to run_race.py")
    parser.add_argument("--python", default=sys.executable, help="Python executable for child commands")
    parser.add_argument("--results-dir", help="Campaign output directory (default: results/campaigns/<auto>)")
    parser.add_argument("--limit", type=int, help="Optional limit on number of scenarios (for batches/testing)")
    parser.add_argument("--skip-missing", action="store_true", help="Pass --skip-missing to run_race.py")
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue campaign when one scenario fails",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print/record commands without executing")
    parser.add_argument(
        "--no-postprocess",
        action="store_true",
        help="Skip postprocess generation (coverage + summary reports)",
    )
    args = parser.parse_args()

    results_dir = resolve_results_dir(args.results_dir, args.agents, args.variant)
    results_dir.mkdir(parents=True, exist_ok=True)

    progress_file = results_dir / "progress.json"
    events_file = results_dir / "campaign_events.jsonl"
    summary_file = results_dir / "summary.json"

    config = {
        "python_exe": args.python,
        "agents": args.agents,
        "variant": args.variant,
        "seed": args.seed,
        "max_turns": args.max_turns,
        "dry_run": args.dry_run,
    }
    progress = load_progress(progress_file, config=config)

    specs = sorted(SCENARIOS, key=lambda s: s.simulation_id)
    if args.limit is not None:
        specs = specs[: max(args.limit, 0)]

    total = len(specs)
    print(f"Campaign dir: {results_dir}")
    print(f"Scenarios selected: {total}")
    print(f"Resume mode: existing successful runs will be skipped")

    for idx, spec in enumerate(specs, start=1):
        simulation_id = spec.simulation_id
        if already_successful(progress, simulation_id):
            print(f"[{idx}/{total}] SKIP {simulation_id} (already successful)")
            continue

        results_file = results_dir / f"{simulation_id}.json"
        cmd = build_run_command(
            python_exe=args.python,
            agents=args.agents,
            simulation_id=simulation_id,
            variant=args.variant,
            seed=args.seed,
            max_turns=args.max_turns,
            results_file=results_file,
            skip_missing=args.skip_missing,
        )
        print(f"[{idx}/{total}] RUN {simulation_id}")
        print("CMD:", " ".join(cmd))
        started = time.time()
        rc = run_cmd(cmd=cmd, cwd=REPO_ROOT, dry_run=args.dry_run)
        elapsed = round(time.time() - started, 2)

        row = {
            "simulation": simulation_id,
            "returncode": int(rc),
            "elapsed_seconds": elapsed,
            "results_file": str(results_file),
            "timestamp_utc": utc_now(),
            "command": cmd,
        }
        progress.setdefault("runs", []).append(row)
        save_json(progress_file, progress)
        append_event(events_file, row)
        print(f"[{idx}/{total}] {'OK' if rc == 0 else 'FAIL'} {simulation_id} rc={rc} elapsed={elapsed}s")

        if rc != 0 and not args.continue_on_failure:
            print("Stopping after first failure. Use --continue-on-failure to keep going.")
            break

    summary = build_campaign_summary(results_dir=results_dir, config=config, progress=progress)
    save_json(summary_file, summary)
    print(f"Campaign summary saved to {summary_file}")

    if not args.no_postprocess and not args.dry_run:
        quality = postprocess(results_dir=results_dir, python_exe=args.python, progress=progress)
        print(f"Postprocess quality report saved to {results_dir / 'quality_report.json'}")
        if quality.get("coverage_ratio") is not None:
            print(
                "Coverage:",
                f"{quality.get('coverage_with_results')}/{quality.get('coverage_total')}",
                f"({quality.get('coverage_ratio'):.1%})",
            )

    failures = int(summary["runs_failed"])
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
