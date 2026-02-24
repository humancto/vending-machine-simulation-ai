#!/usr/bin/env python3
"""Summarize race artifact coverage across simulations, variants, and agents."""

from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from race.scenario_registry import scenario_ids


def _load_records(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict)]


def _normalize_agent_type(row: dict) -> str | None:
    atype = row.get("agent_type")
    if isinstance(atype, str) and atype:
        return atype
    agent_name = row.get("agent")
    if isinstance(agent_name, str):
        lowered = agent_name.lower()
        if "claude" in lowered:
            return "claude"
        if "codex" in lowered:
            return "codex"
        if "gemini" in lowered:
            return "gemini"
    return None


def build_coverage(results_glob: str) -> dict[str, Any]:
    known_sims = sorted(scenario_ids())
    known_set = set(known_sims)

    search_pattern = results_glob
    if not Path(results_glob).is_absolute():
        search_pattern = str(REPO_ROOT / results_glob)
    files = sorted(Path(p) for p in glob.glob(search_pattern, recursive=True))
    files_scanned = 0
    records_scanned = 0

    by_sim_records: dict[str, int] = defaultdict(int)
    by_sim_variants: dict[str, set[str]] = defaultdict(set)
    by_sim_seeds: dict[str, set[int]] = defaultdict(set)
    by_sim_agents: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    unknown_simulations: dict[str, int] = defaultdict(int)

    for path in files:
        if not path.is_file():
            continue
        files_scanned += 1
        for record in _load_records(path):
            simulation = record.get("simulation")
            results = record.get("results")
            if not isinstance(simulation, str) or not isinstance(results, list):
                continue
            records_scanned += 1

            if simulation not in known_set:
                unknown_simulations[simulation] += 1
                continue

            by_sim_records[simulation] += 1
            variant = record.get("variant")
            if isinstance(variant, str) and variant:
                by_sim_variants[simulation].add(variant)
            seed = record.get("seed")
            if isinstance(seed, int):
                by_sim_seeds[simulation].add(seed)

            for row in results:
                if not isinstance(row, dict):
                    continue
                atype = _normalize_agent_type(row)
                if atype:
                    by_sim_agents[simulation][atype] += 1

    simulations_with_results = sorted(sim for sim in known_sims if by_sim_records.get(sim, 0) > 0)
    missing = sorted(sim for sim in known_sims if by_sim_records.get(sim, 0) == 0)

    per_sim = []
    for sim in known_sims:
        if by_sim_records.get(sim, 0) == 0:
            continue
        per_sim.append(
            {
                "simulation": sim,
                "record_count": by_sim_records[sim],
                "seed_count": len(by_sim_seeds[sim]),
                "variants": sorted(by_sim_variants[sim]),
                "agent_counts": dict(sorted(by_sim_agents[sim].items())),
            }
        )

    return {
        "schema_version": "results_coverage_v1",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results_glob": results_glob,
        "files_scanned": files_scanned,
        "records_scanned": records_scanned,
        "simulations_total": len(known_sims),
        "simulations_with_results": len(simulations_with_results),
        "coverage_ratio": round(
            (len(simulations_with_results) / len(known_sims)) if known_sims else 0.0,
            3,
        ),
        "simulations_missing": missing,
        "unknown_simulation_records": dict(sorted(unknown_simulations.items())),
        "per_simulation": per_sim,
    }


def print_human(payload: dict[str, Any]) -> None:
    print("Results Coverage Summary")
    print("========================")
    print(f"Files scanned: {payload['files_scanned']}")
    print(f"Records scanned: {payload['records_scanned']}")
    print(
        "Simulations with results: "
        f"{payload['simulations_with_results']}/{payload['simulations_total']} "
        f"({payload['coverage_ratio']:.1%})"
    )
    print(f"Simulations missing: {len(payload['simulations_missing'])}")
    if payload["simulations_missing"]:
        print("Missing IDs:", ", ".join(payload["simulations_missing"]))
    print("")
    print(f"{'Simulation':<32} {'Records':>8} {'Seeds':>7} {'Variants':<28} {'Agents'}")
    print("-" * 108)
    for row in payload["per_simulation"]:
        agent_label = ", ".join(
            f"{agent}:{count}" for agent, count in sorted(row["agent_counts"].items())
        )
        variant_label = ",".join(row["variants"])
        print(
            f"{row['simulation']:<32} {row['record_count']:>8} {row['seed_count']:>7} "
            f"{variant_label[:28]:<28} {agent_label}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize simulation coverage from saved race result artifacts."
    )
    parser.add_argument(
        "--results-glob",
        default="results/**/*.json",
        help="Glob (relative to repo root) for result JSON files.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output file path.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print JSON summary to stdout.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress human-readable output.",
    )
    parser.add_argument(
        "--min-simulations-with-results",
        type=int,
        help="Fail (exit 1) if fewer than this many simulations have result artifacts.",
    )
    args = parser.parse_args()

    payload = build_coverage(args.results_glob)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Coverage summary saved to {output_path}")

    if not args.quiet:
        print_human(payload)

    if args.print_json:
        print(json.dumps(payload, indent=2))

    if (
        args.min_simulations_with_results is not None
        and payload["simulations_with_results"] < args.min_simulations_with_results
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
