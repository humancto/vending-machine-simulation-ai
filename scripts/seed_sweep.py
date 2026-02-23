#!/usr/bin/env python3
"""Run repeated race evaluations over a seed list and emit reproducible artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from race.scenario_registry import get_scenario


def parse_seed_list(raw: str) -> list[int]:
    seeds: list[int] = []
    seen: set[int] = set()
    for token in raw.replace(",", " ").split():
        seed = int(token)
        if seed in seen:
            continue
        seen.add(seed)
        seeds.append(seed)
    if not seeds:
        raise ValueError("At least one seed is required")
    return seeds


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def build_run_command(
    python_exe: str,
    simulation: str,
    agents: str,
    variant: str,
    max_turns: int,
    duration_arg: str,
    duration_value: int,
    seed: int,
    results_file: Path,
    no_constraints: bool,
) -> list[str]:
    cmd = [
        python_exe,
        "run_race.py",
        "--agents",
        agents,
        "--simulation",
        simulation,
        "--variant",
        variant,
        "--seed",
        str(seed),
        f"--{duration_arg}",
        str(duration_value),
        "--max-turns",
        str(max_turns),
        "--results-file",
        str(results_file),
    ]
    if no_constraints:
        cmd.append("--no-constraints")
    return cmd


def run_cmd(cmd: list[str], cwd: Path, dry_run: bool) -> int:
    if dry_run:
        return 0
    completed = subprocess.run(cmd, cwd=cwd)
    return int(completed.returncode)


def main() -> int:
    repo_root = REPO_ROOT

    parser = argparse.ArgumentParser(
        description="Run run_race.py across multiple seeds and collect summarized artifacts."
    )
    parser.add_argument("--agents", required=True, help="Comma-separated agent types (e.g. codex,claude)")
    parser.add_argument("--simulation", required=True, help="Scenario id from race/scenario_registry.py")
    parser.add_argument(
        "--seeds",
        required=True,
        help="Seed list, comma or space separated (example: '1,2,3,4').",
    )
    parser.add_argument("--variant", default="soft_guidelines", help="Constraint variant")
    parser.add_argument(
        "--duration",
        type=int,
        help="Override simulation duration. Defaults to registry default_duration.",
    )
    parser.add_argument("--max-turns", type=int, default=200, help="Max turns for each agent run")
    parser.add_argument(
        "--results-dir",
        help=(
            "Output directory. Default: "
            "results/seed_sweeps/<simulation>/<variant>/<timestamp>"
        ),
    )
    parser.add_argument("--python", default=sys.executable, help="Python executable for child commands")
    parser.add_argument("--metric", default="composite_score", help="Metric for summary script")
    parser.add_argument(
        "--group-by",
        default="simulation,variant,agent_type,effective_model",
        help="Group keys for summary script",
    )
    parser.add_argument(
        "--baseline-file",
        help="Optional baseline for regression_gate.py against generated summary",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue remaining seeds if one run fails.",
    )
    parser.add_argument("--no-constraints", action="store_true", help="Pass --no-constraints to run_race.py")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing.")
    args = parser.parse_args()

    spec = get_scenario(args.simulation)
    seeds = parse_seed_list(args.seeds)
    duration_value = args.duration if args.duration is not None else spec.default_duration

    if args.results_dir:
        results_dir = Path(args.results_dir)
        if not results_dir.is_absolute():
            results_dir = repo_root / results_dir
    else:
        results_dir = (
            repo_root
            / "results"
            / "seed_sweeps"
            / args.simulation
            / args.variant
            / now_stamp()
        )
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"Simulation: {args.simulation} ({spec.display_name})")
    print(f"Variant: {args.variant}")
    print(f"Seeds: {seeds}")
    print(f"Duration: {duration_value} ({spec.duration_arg})")
    print(f"Results dir: {results_dir}")
    print(f"Dry run: {args.dry_run}")

    run_rows: list[dict] = []
    for seed in seeds:
        result_file = results_dir / f"seed_{seed}.json"
        cmd = build_run_command(
            python_exe=args.python,
            simulation=args.simulation,
            agents=args.agents,
            variant=args.variant,
            max_turns=args.max_turns,
            duration_arg=spec.duration_arg,
            duration_value=duration_value,
            seed=seed,
            results_file=result_file,
            no_constraints=args.no_constraints,
        )
        print("\nRUN:", " ".join(cmd))
        rc = run_cmd(cmd=cmd, cwd=repo_root, dry_run=args.dry_run)
        run_rows.append(
            {
                "seed": seed,
                "returncode": rc,
                "command": cmd,
                "results_file": str(result_file),
            }
        )
        if rc != 0 and not args.continue_on_failure:
            print(f"Stopping on first failure (seed={seed}, returncode={rc})")
            break

    summary_file = results_dir / "summary.json"
    summary_returncode = None
    gate_returncode = None

    successful_results = [row["results_file"] for row in run_rows if row["returncode"] == 0]
    if successful_results:
        summary_cmd = [args.python, "scripts/summarize_results.py"]
        for results_file in successful_results:
            summary_cmd.extend(["--results-file", results_file])
        summary_cmd.extend(
            [
                "--metric",
                args.metric,
                "--group-by",
                args.group_by,
                "--output",
                str(summary_file),
                "--quiet",
            ]
        )
        print("\nSUMMARY:", " ".join(summary_cmd))
        summary_returncode = run_cmd(summary_cmd, cwd=repo_root, dry_run=args.dry_run)

        if args.baseline_file and summary_returncode == 0:
            gate_cmd = [
                args.python,
                "scripts/regression_gate.py",
                "--summary-file",
                str(summary_file),
                "--baseline-file",
                args.baseline_file,
            ]
            print("\nGATE:", " ".join(gate_cmd))
            gate_returncode = run_cmd(gate_cmd, cwd=repo_root, dry_run=args.dry_run)

    manifest = {
        "schema_version": "seed_sweep_manifest_v1",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "simulation": args.simulation,
        "variant": args.variant,
        "duration_arg": spec.duration_arg,
        "duration_value": duration_value,
        "agents": args.agents,
        "seeds": seeds,
        "metric": args.metric,
        "group_by": args.group_by,
        "dry_run": args.dry_run,
        "runs": run_rows,
        "summary_file": str(summary_file),
        "summary_returncode": summary_returncode,
        "baseline_file": args.baseline_file,
        "gate_returncode": gate_returncode,
    }
    manifest_path = results_dir / "seed_sweep_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest saved to {manifest_path}")

    if any(row["returncode"] != 0 for row in run_rows):
        return 1
    if summary_returncode not in (None, 0):
        return int(summary_returncode)
    if gate_returncode not in (None, 0):
        return int(gate_returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
