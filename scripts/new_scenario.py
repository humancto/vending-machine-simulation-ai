#!/usr/bin/env python3
"""Scaffold a new simulation package, prompt set, CLI, and test stub.

This is designed for fast contributor onboarding. By default it also appends
the scenario to race/scenario_registry.py.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

VALID_DURATION_ARGS = {
    "days": ("Days", 90),
    "hours": ("Hours", 72),
    "weeks": ("Weeks", 8),
    "months": ("Months", 24),
    "quarters": ("Quarters", 12),
    "rounds": ("Rounds", 100),
    "sessions": ("Sessions", 10),
    "hands": ("Hands", 20),
    "seasons": ("Seasons", 30),
    "years": ("Years", 30),
}


def _validate_identifier(value: str, name: str, pattern: str) -> str:
    if not re.fullmatch(pattern, value):
        raise ValueError(f"Invalid {name}: {value!r}")
    return value


def _write_file(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"[ok] wrote {path}")


def _ensure_missing(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Path exists (use --force to overwrite): {path}")


def _registry_line(
    simulation_id: str,
    title: str,
    duration_arg: str,
    duration_label: str,
    default_duration: int,
    prompt_code: str,
    cli_code: str | None,
) -> str:
    if cli_code and cli_code != prompt_code:
        return (
            f'    ScenarioSpec("{simulation_id}", "{title}", "{duration_arg}", '
            f'"{duration_label}", {default_duration}, "{prompt_code}", "{cli_code}"),\n'
        )
    return (
        f'    ScenarioSpec("{simulation_id}", "{title}", "{duration_arg}", '
        f'"{duration_label}", {default_duration}, "{prompt_code}"),\n'
    )


def _update_registry(
    simulation_id: str,
    title: str,
    duration_arg: str,
    duration_label: str,
    default_duration: int,
    prompt_code: str,
    cli_code: str | None,
    dry_run: bool,
) -> None:
    registry_path = ROOT / "race" / "scenario_registry.py"
    text = registry_path.read_text()
    if f'ScenarioSpec("{simulation_id}"' in text:
        raise ValueError(f"Simulation id already in registry: {simulation_id}")
    if f'"{prompt_code}"),' in text or f'"{prompt_code}", "' in text:
        raise ValueError(f"Prompt code already in registry: {prompt_code}")
    if cli_code and (f'"{cli_code}"),' in text or f'", "{cli_code}")' in text):
        raise ValueError(f"CLI code appears to be in registry already: {cli_code}")

    marker = "\n)\n\nSCENARIO_BY_ID"
    idx = text.find(marker)
    if idx < 0:
        raise RuntimeError("Could not locate SCENARIOS tuple boundary in race/scenario_registry.py")

    insert = _registry_line(
        simulation_id,
        title,
        duration_arg,
        duration_label,
        default_duration,
        prompt_code,
        cli_code,
    )
    updated = text[:idx] + insert + text[idx:]
    if dry_run:
        print(f"[dry-run] update {registry_path} with: {insert.strip()}")
        return
    registry_path.write_text(updated)
    print(f"[ok] updated {registry_path}")


def scaffold(
    simulation_id: str,
    prompt_code: str,
    cli_code: str,
    title: str,
    duration_arg: str,
    duration_label: str,
    default_duration: int,
    dry_run: bool,
    force: bool,
    no_registry: bool,
) -> None:
    prompt_dir = ROOT / "prompts" / simulation_id
    sim_dir = ROOT / "simulations" / simulation_id
    cli_path = ROOT / "sim_cli" / f"{cli_code}_cli.py"
    test_path = ROOT / "tests" / f"test_{cli_code}_cli.py"

    targets = [
        prompt_dir / "unconstrained.md",
        prompt_dir / "soft_guidelines.md",
        prompt_dir / "hard_rules.md",
        sim_dir / "__init__.py",
        sim_dir / "simulation.py",
        cli_path,
        test_path,
    ]
    for path in targets:
        _ensure_missing(path, force)

    for variant, extra in (
        ("unconstrained", "No additional policy constraints."),
        ("soft_guidelines", "Prefer ethical actions where feasible."),
        ("hard_rules", "Hard policy constraints are enforced."),
    ):
        _write_file(
            prompt_dir / f"{variant}.md",
            (
                f"# {title}\n\n"
                f"Scenario: `{simulation_id}`\n"
                f"Variant: `{variant}`\n\n"
                f"{extra}\n\n"
                "Use only CLI actions for this simulation and complete the full run horizon.\n"
            ),
            dry_run=dry_run,
        )

    _write_file(sim_dir / "__init__.py", '"""Simulation package."""\n', dry_run=dry_run)
    _write_file(
        sim_dir / "simulation.py",
        (
            '"""Core simulation logic for this scenario."""\n\n\n'
            "class PlaceholderSimulation:\n"
            "    def __init__(self, seed=None, variant='soft_guidelines'):\n"
            "        self.seed = seed\n"
            "        self.variant = variant\n"
        ),
        dry_run=dry_run,
    )

    _write_file(
        cli_path,
        (
            "#!/usr/bin/env python3\n"
            f'"""CLI for {title} ({simulation_id})."""\n\n'
            "import argparse\n\n\n"
            "def build_parser():\n"
            f"    parser = argparse.ArgumentParser(description='{title} CLI')\n"
            "    sub = parser.add_subparsers(dest='cmd', required=True)\n"
            "    sub.add_parser('start')\n"
            "    sub.add_parser('status')\n"
            "    sub.add_parser('advance')\n"
            "    sub.add_parser('full-score')\n"
            "    return parser\n\n\n"
            "def main():\n"
            "    parser = build_parser()\n"
            "    args = parser.parse_args()\n"
            "    if args.cmd == 'full-score':\n"
            "        print('{\"composite_score\": 0}')\n"
            "        return 0\n"
            "    print('Not implemented yet')\n"
            "    return 1\n\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        ),
        dry_run=dry_run,
    )

    _write_file(
        test_path,
        (
            f'"""Smoke scaffold test for {cli_code}_cli.py."""\n\n'
            "import pytest\n\n\n"
            "@pytest.mark.skip(reason='Scenario scaffold only; implement tests in PR')\n"
            "def test_placeholder():\n"
            "    assert True\n"
        ),
        dry_run=dry_run,
    )

    if not no_registry:
        _update_registry(
            simulation_id=simulation_id,
            title=title.upper(),
            duration_arg=duration_arg,
            duration_label=duration_label,
            default_duration=default_duration,
            prompt_code=prompt_code,
            cli_code=cli_code,
            dry_run=dry_run,
        )

    print("\nNext steps:")
    print("1. Implement simulations/<id>/simulation.py and sim_cli/<code>_cli.py behavior.")
    print("2. Replace scaffold tests with real CLI + simulation tests.")
    print("3. Add scenario docs and run full validation before opening PR.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new Simulation Crucible scenario")
    parser.add_argument("--id", required=True, help="Scenario id (e.g. grid_failure)")
    parser.add_argument("--code", required=True, help="Short prompt code (e.g. gf)")
    parser.add_argument("--cli-code", default=None, help="Optional CLI module code if different from prompt code")
    parser.add_argument("--title", required=True, help="Display title (e.g. Grid Failure Response)")
    parser.add_argument(
        "--duration-arg",
        required=True,
        choices=sorted(VALID_DURATION_ARGS),
        help="Primary horizon argument used by run_race.py",
    )
    parser.add_argument("--duration-label", default=None, help="Label shown in race output (defaults from duration arg)")
    parser.add_argument("--default-duration", type=int, default=None, help="Default horizon for docs/registry metadata")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files if they already exist")
    parser.add_argument("--no-registry", action="store_true", help="Do not auto-append scenario to race/scenario_registry.py")
    args = parser.parse_args()

    simulation_id = _validate_identifier(args.id.strip(), "scenario id", r"[a-z][a-z0-9_]*")
    prompt_code = _validate_identifier(args.code.strip(), "scenario code", r"[a-z][a-z0-9]*")
    cli_code = _validate_identifier(
        (args.cli_code or args.code).strip(),
        "cli code",
        r"[a-z][a-z0-9]*",
    )

    default_label, default_duration = VALID_DURATION_ARGS[args.duration_arg]
    duration_label = args.duration_label or default_label
    duration_default_value = args.default_duration if args.default_duration is not None else default_duration

    try:
        scaffold(
            simulation_id=simulation_id,
            prompt_code=prompt_code,
            cli_code=cli_code,
            title=args.title.strip(),
            duration_arg=args.duration_arg,
            duration_label=duration_label,
            default_duration=duration_default_value,
            dry_run=args.dry_run,
            force=args.force,
            no_registry=args.no_registry,
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
