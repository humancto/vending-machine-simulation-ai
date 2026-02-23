#!/usr/bin/env python3
"""Create scenario-based prompt layout from legacy AGENT_*.md files.

This script is idempotent and keeps legacy files untouched.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from race.scenario_registry import PROMPT_CODE_TO_SCENARIO

PROMPTS_DIR = ROOT / "prompts"
LEGACY_DIR = PROMPTS_DIR / "_legacy"


def copy_if_exists(src: Path, dst: Path):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def copy_from_sources(filename: str, dst: Path):
    """Copy from repo root first, then prompts/_legacy fallback."""
    root_src = ROOT / filename
    if root_src.exists():
        return copy_if_exists(root_src, dst)
    legacy_src = LEGACY_DIR / filename
    return copy_if_exists(legacy_src, dst)


def main() -> int:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0

    # Vending machine (legacy unprefixed AGENT files)
    vending = PROMPTS_DIR / "vending_machine"
    copied += int(copy_from_sources("AGENT.md", vending / "default.md"))
    copied += int(copy_from_sources("AGENT_unconstrained.md", vending / "unconstrained.md"))
    copied += int(copy_from_sources("AGENT_soft.md", vending / "soft_guidelines.md"))
    copied += int(copy_from_sources("AGENT_hard.md", vending / "hard_rules.md"))

    # Scenario prompts by short code
    for code, scenario in PROMPT_CODE_TO_SCENARIO.items():
        scenario_dir = PROMPTS_DIR / scenario
        copied += int(copy_from_sources(f"AGENT_{code}_unconstrained.md", scenario_dir / "unconstrained.md"))
        copied += int(copy_from_sources(f"AGENT_{code}_soft.md", scenario_dir / "soft_guidelines.md"))
        copied += int(copy_from_sources(f"AGENT_{code}_hard.md", scenario_dir / "hard_rules.md"))

    readme = PROMPTS_DIR / "README.md"
    readme.write_text(
        "# Scenario Prompt Layout\n\n"
        "Each scenario has three variants:\n"
        "- `unconstrained.md`\n"
        "- `soft_guidelines.md`\n"
        "- `hard_rules.md`\n"
    )

    print(f"Prompt migration complete. Files copied: {copied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
