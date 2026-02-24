#!/usr/bin/env python3
"""Clone-and-run readiness checks for Simulation Crucible."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from race import orchestrator, preflight


REQUIRED_IMPORTS = {
    "flask": "Flask",
    "flask_socketio": "Flask-SocketIO",
    "jsonschema": "jsonschema",
}


def _run_help(cmd: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return False, str(exc)
    if completed.returncode == 0:
        return True, "ok"
    details = (completed.stderr or completed.stdout or "failed").strip()
    return False, details[:160]


def _check_python() -> tuple[bool, str]:
    version = sys.version_info
    ok = (version.major, version.minor) >= (3, 8)
    text = f"{version.major}.{version.minor}.{version.micro}"
    if ok:
        return True, text
    return False, f"{text} (requires >=3.8)"


def _check_imports() -> tuple[bool, dict[str, dict[str, Any]]]:
    checks: dict[str, dict[str, Any]] = {}
    all_ok = True
    for module_name, display in REQUIRED_IMPORTS.items():
        try:
            __import__(module_name)
            checks[module_name] = {"ok": True, "display": display, "error": ""}
        except Exception as exc:  # pragma: no cover - import errors are environment-dependent
            all_ok = False
            checks[module_name] = {
                "ok": False,
                "display": display,
                "error": str(exc),
            }
    return all_ok, checks


def _check_agents(agent_types: list[str]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for atype in agent_types:
        available, version, error = preflight.check_agent_available(
            orchestrator.AGENT_DEFS, atype
        )
        key_set, key_name = preflight.check_api_key(orchestrator.AGENT_DEFS, atype)
        model, model_source = preflight.detect_model(atype)
        results[atype] = {
            "available": available,
            "version": version,
            "error": error,
            "api_key_set": key_set,
            "api_key_name": key_name,
            "model": model,
            "model_source": model_source,
            "binary_found": bool(
                shutil.which((orchestrator.AGENT_DEFS.get(atype) or {}).get("binary", ""))
            ),
        }
    return results


def _parse_agents(raw: str) -> list[str]:
    seen: set[str] = set()
    parsed: list[str] = []
    for token in raw.replace(",", " ").split():
        name = token.strip().lower()
        if not name or name in seen:
            continue
        seen.add(name)
        parsed.append(name)
    return parsed


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    python_ok, python_info = _check_python()
    imports_ok, imports = _check_imports()
    run_race_ok, run_race_info = _run_help([sys.executable, "run_race.py", "--help"])
    run_bench_ok, run_bench_info = _run_help(
        [sys.executable, "run_benchmark.py", "--help"]
    )
    core_ready = python_ok and imports_ok and run_race_ok and run_bench_ok

    selected_agents = _parse_agents(args.agents)
    agent_results: dict[str, dict[str, Any]] = {}
    any_agent_available = False
    all_agents_available = True
    race_ready = True

    if not args.skip_agents:
        agent_results = _check_agents(selected_agents)
        any_agent_available = any(
            info.get("available", False) for info in agent_results.values()
        )
        all_agents_available = all(
            info.get("available", False) for info in agent_results.values()
        )
        race_ready = any_agent_available
    else:
        any_agent_available = False
        all_agents_available = False
        race_ready = False

    exit_code = 0
    if not core_ready:
        exit_code = 1
    elif args.strict_race and not race_ready:
        exit_code = 1
    elif args.require_all and not all_agents_available:
        exit_code = 1

    payload: dict[str, Any] = {
        "schema_version": "doctor_v1",
        "repo_root": str(REPO_ROOT),
        "core": {
            "python_ok": python_ok,
            "python_info": python_info,
            "imports_ok": imports_ok,
            "imports": imports,
            "run_race_help_ok": run_race_ok,
            "run_race_help_info": run_race_info,
            "run_benchmark_help_ok": run_bench_ok,
            "run_benchmark_help_info": run_bench_info,
            "core_ready": core_ready,
        },
        "agents": {
            "checked": not args.skip_agents,
            "selected": selected_agents,
            "any_available": any_agent_available,
            "all_available": all_agents_available,
            "race_ready": race_ready,
            "details": agent_results,
        },
        "exit_code": exit_code,
    }
    return exit_code, payload


def print_human(payload: dict[str, Any]) -> None:
    core = payload["core"]
    agents = payload["agents"]

    print("Simulation Crucible Doctor")
    print("==========================")
    print(f"Core readiness: {_status(core['core_ready'])}")
    print(f"  Python >=3.8: {_status(core['python_ok'])} ({core['python_info']})")
    print(f"  Required imports: {_status(core['imports_ok'])}")
    for module_name, info in core["imports"].items():
        print(f"    - {info['display']} ({module_name}): {_status(info['ok'])}")
    print(
        f"  run_race.py --help: {_status(core['run_race_help_ok'])} "
        f"({core['run_race_help_info']})"
    )
    print(
        f"  run_benchmark.py --help: {_status(core['run_benchmark_help_ok'])} "
        f"({core['run_benchmark_help_info']})"
    )

    if agents["checked"]:
        print(f"Race readiness (>=1 selected agent available): {_status(agents['race_ready'])}")
        print(
            "All selected agents available: "
            f"{_status(agents['all_available'])}"
        )
        for atype in agents["selected"]:
            info = agents["details"].get(atype, {})
            available = info.get("available", False)
            version_or_error = info.get("version") or info.get("error") or ""
            print(f"  - {atype}: {_status(available)} {version_or_error}")
            if info.get("api_key_name"):
                print(
                    "      auth env set: "
                    f"{_status(info.get('api_key_set', False))} "
                    f"({info['api_key_name']})"
                )
            print(
                "      model: "
                f"{info.get('model', 'unknown')} ({info.get('model_source', 'unknown')})"
            )
    else:
        print("Race readiness: SKIPPED (--skip-agents)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether this clone is ready for local demo and/or race runs."
    )
    parser.add_argument(
        "--agents",
        default="claude,codex,gemini",
        help="Comma-separated agent types to check (default: claude,codex,gemini).",
    )
    parser.add_argument(
        "--skip-agents",
        action="store_true",
        help="Skip agent CLI/auth checks and only validate core local setup.",
    )
    parser.add_argument(
        "--strict-race",
        action="store_true",
        help="Exit non-zero unless at least one selected agent is available.",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Exit non-zero unless all selected agents are available.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    args = parser.parse_args()

    exit_code, payload = run(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
