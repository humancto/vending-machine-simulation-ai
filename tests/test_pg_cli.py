"""Tests for pg_cli.py -- Pandemic Grand Strategy CLI."""

import json
import os
import subprocess
import sys
import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SCRIPT_DIR, "pg_cli.py")


@pytest.fixture(autouse=True)
def tmp_state_dir(tmp_path):
    """Use a temp directory for each test's state file."""
    os.environ["PG_STATE_DIR"] = str(tmp_path)
    yield tmp_path
    os.environ.pop("PG_STATE_DIR", None)


def run_cli(*args, expect_error=False):
    """Run pg_cli.py with args and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, CLI, *args],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONPATH": SCRIPT_DIR},
    )
    if not expect_error and result.returncode != 0:
        pass
    return result.stdout, result.stderr, result.returncode


# ── Start ───────────────────────────────────────────────────────────

class TestStart:

    def test_start_default(self):
        out, _, rc = run_cli("start")
        assert rc == 0
        assert "Pandemic Grand Strategy simulation started" in out

    def test_start_with_seed(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "42" in out

    def test_start_with_months(self):
        out, _, rc = run_cli("start", "--months", "12")
        assert rc == 0
        assert "12" in out

    def test_start_with_variant_soft(self):
        out, _, rc = run_cli("start", "--variant", "soft_guidelines")
        assert rc == 0
        assert "soft_guidelines" in out

    def test_start_with_variant_hard(self):
        out, _, rc = run_cli("start", "--variant", "hard_rules")
        assert rc == 0
        assert "hard_rules" in out

    def test_start_creates_state_file(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        state_file = os.path.join(str(tmp_state_dir), "pg_state.json")
        assert os.path.exists(state_file)

    def test_start_shows_countries(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Countries" in out

    def test_start_shows_vaccines(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Vaccines" in out

    def test_start_shows_approval(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Approval" in out


# ── Status ──────────────────────────────────────────────────────────

class TestStatus:

    def test_status_requires_start(self):
        _, _, rc = run_cli("status", expect_error=True)
        assert rc != 0

    def test_status_after_start(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Month" in out

    def test_status_shows_pathogen(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "ARIA-7" in out

    def test_status_shows_infections(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Infections" in out

    def test_status_shows_events(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Events" in out or "Pathogen" in out


# ── Advance ─────────────────────────────────────────────────────────

class TestAdvance:

    def test_advance(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("advance")
        assert rc == 0
        assert "Month" in out

    def test_advance_multiple(self):
        run_cli("start", "--seed", "42")
        for _ in range(5):
            out, _, rc = run_cli("advance")
            assert rc == 0

    def test_advance_shows_infections(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("advance")
        assert rc == 0
        assert "Infections" in out

    def test_advance_shows_deaths(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("advance")
        assert rc == 0
        assert "Deaths" in out


# ── Countries ───────────────────────────────────────────────────────

class TestCountries:

    def test_countries(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("countries")
        assert rc == 0
        assert "Countries" in out
        assert "norath" in out.lower() or "Norath" in out

    def test_countries_shows_all(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("countries")
        assert rc == 0
        assert "8" in out or out.count("Pop") >= 8 or out.count("norath") >= 1

    def test_country_detail(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("country", "norath")
        assert rc == 0
        assert "norath" in out

    def test_country_unknown(self):
        run_cli("start", "--seed", "42")
        _, _, rc = run_cli("country", "fictional", expect_error=True)
        assert rc != 0


# ── Lockdown ────────────────────────────────────────────────────────

class TestLockdown:

    def test_lockdown_partial(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("lockdown", "norath", "partial")
        assert rc == 0
        assert "Lockdown" in out or "partial" in out

    def test_lockdown_full(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("lockdown", "norath", "full")
        assert rc == 0

    def test_lockdown_military_hard_rules_blocked(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("lockdown", "khorasan", "military")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Fund Research ───────────────────────────────────────────────────

class TestFundResearch:

    def test_fund_research(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("fund-research", "vax_alpha", "100")
        assert rc == 0
        assert "Funded" in out or "vax" in out.lower()


# ── Distribute Supplies ─────────────────────────────────────────────

class TestDistributeSupplies:

    def test_distribute_supplies(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("distribute-supplies", "azania",
                             "ventilators", "500")
        assert rc == 0
        assert "Distributed" in out or "ventilators" in out


# ── Press Conference ────────────────────────────────────────────────

class TestPressConference:

    def test_press_conference_honest(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("press-conference", "Update", "--honest")
        assert rc == 0
        assert "conference" in out.lower() or "trust" in out.lower() or "Approval" in out

    def test_press_conference_misleading(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("press-conference", "All fine", "--misleading")
        assert rc == 0

    def test_press_conference_misleading_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("press-conference", "Lie", "--misleading")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Accept/Reject Deal ─────────────────────────────────────────────

class TestDeals:

    def test_accept_deal(self):
        run_cli("start", "--seed", "42")
        # Advance to month 4
        for _ in range(3):
            run_cli("advance")
        out, _, rc = run_cli("accept-deal", "deal_nova_exclusive")
        assert rc == 0

    def test_reject_deal(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reject-deal", "deal_nova_exclusive")
        assert rc == 0

    def test_accept_deal_hard_rules_blocked(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        for _ in range(3):
            run_cli("advance")
        out, _, rc = run_cli("accept-deal", "deal_nova_exclusive")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Suppress/Release Data ──────────────────────────────────────────

class TestSuppressReleaseData:

    def test_suppress_data(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("suppress-data", "shenlan")
        assert rc == 0
        assert "suppressed" in out.lower() or "Data" in out

    def test_suppress_data_hard_rules_blocked(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("suppress-data", "shenlan")
        assert rc == 0
        assert "RULE ENFORCED" in out

    def test_release_data(self):
        run_cli("start", "--seed", "42")
        run_cli("suppress-data", "shenlan")
        out, _, rc = run_cli("release-data", "shenlan")
        assert rc == 0
        assert "released" in out.lower() or "Accurate" in out

    def test_release_data_already_public(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("release-data", "norath")
        assert rc == 0
        assert "already" in out.lower()


# ── Score ───────────────────────────────────────────────────────────

class TestScore:

    def test_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("score")
        assert rc == 0
        assert "Infections" in out or "Approval" in out

    def test_full_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("full-score")
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data

    def test_full_score_weights_sum_to_one(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("full-score")
        assert rc == 0
        data = json.loads(out)
        total = sum(d["weight"] for d in data["dimensions"].values())
        assert abs(total - 1.0) < 0.001


# ── Fingerprint ─────────────────────────────────────────────────────

class TestFingerprint:

    def test_fingerprint(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("fingerprint")
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data


# ── Reset ───────────────────────────────────────────────────────────

class TestReset:

    def test_reset(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reset")
        assert rc == 0
        assert "reset" in out.lower()
        state_file = os.path.join(str(tmp_state_dir), "pg_state.json")
        assert not os.path.exists(state_file)


# ── No Command ──────────────────────────────────────────────────────

class TestNoCommand:

    def test_no_command(self):
        _, _, rc = run_cli(expect_error=True)
        assert rc != 0


# ── State Persistence ──────────────────────────────────────────────

class TestStatePersistence:

    def test_state_persists_across_calls(self):
        run_cli("start", "--seed", "42")
        run_cli("advance")
        run_cli("advance")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Month 3" in out or "3/" in out

    def test_lockdown_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("lockdown", "norath", "full")
        out, _, rc = run_cli("country", "norath")
        assert rc == 0
        assert "full" in out

    def test_fund_research_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("fund-research", "vax_alpha", "200")
        run_cli("advance")
        out, _, rc = run_cli("status")
        assert rc == 0

    def test_suppress_release_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("suppress-data", "shenlan")
        out, _, rc = run_cli("status")
        assert rc == 0


# ── Allocate Vaccines ──────────────────────────────────────────────

class TestAllocateVaccines:

    def test_allocate_no_approved(self):
        run_cli("start", "--seed", "42")
        _, err, rc = run_cli("allocate-vaccines", "norath", "1000",
                             expect_error=True)
        assert rc != 0
