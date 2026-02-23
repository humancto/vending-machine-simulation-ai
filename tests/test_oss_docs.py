"""Contract checks for OSS documentation and governance files."""

import re
from pathlib import Path

from race.scenario_registry import SCENARIOS


ROOT = Path(__file__).resolve().parent.parent


REQUIRED_FILES = [
    "LICENSE",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CONTRIBUTING.md",
    "docs/WHAT_THIS_TESTS.md",
    "docs/TESTING.md",
    "docs/SCREENSHOTS.md",
    "docs/RUNNER_EXTENSION_POINTS.md",
    "race/schemas/race_record_v1.schema.json",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/simulation_proposal.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]


def test_required_oss_files_exist():
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    assert not missing, f"Missing OSS standards files: {missing}"


def test_readme_links_methodology_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/WHAT_THIS_TESTS.md" in readme
    assert "docs/TESTING.md" in readme
    assert "docs/SCREENSHOTS.md" in readme
    assert "docs/RUNNER_EXTENSION_POINTS.md" in readme


def test_readme_scope_claim_boundary_present():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 'It is **not** a universal "gold standard" benchmark.' in readme
    assert "| 51  | First Contact Protocol" not in readme


def test_index_links_methodology_and_has_current_live_count():
    index_html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "Fifty simulations live." in index_html
    assert "Forty-eight simulations live." not in index_html
    assert "docs/WHAT_THIS_TESTS.md" in index_html
    assert "docs/TESTING.md" in index_html


def test_readme_simulation_rows_match_registry_count():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    row_numbers = [int(num) for num in re.findall(r"^\|\s*(\d{1,3})\s*\|", readme, flags=re.M)]
    assert row_numbers, "No numbered simulation rows found in README"
    assert len(row_numbers) == len(SCENARIOS), (
        f"README has {len(row_numbers)} numbered rows but registry has {len(SCENARIOS)} scenarios"
    )
    assert row_numbers == list(range(1, len(SCENARIOS) + 1)), (
        "README numbered simulation rows must stay contiguous and aligned to registry size"
    )
