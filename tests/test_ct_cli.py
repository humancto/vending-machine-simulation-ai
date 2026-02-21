"""Tests for ct_cli.py -- CLI for Climate Tipping Point Council."""

import json
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SCRIPT_DIR, "ct_cli.py")


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Each test gets its own state directory."""
    state_dir = str(tmp_path / "ct_state")
    monkeypatch.setenv("CT_STATE_DIR", state_dir)
    return state_dir


def run_cli(*args, state_dir=None):
    """Run ct_cli.py with given args, return (stdout, stderr, returncode)."""
    env = os.environ.copy()
    if state_dir:
        env["CT_STATE_DIR"] = state_dir
    cmd = [sys.executable, CLI] + list(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, env=env, cwd=SCRIPT_DIR,
    )
    return result.stdout, result.stderr, result.returncode


def start_sim(state_dir, seed=42, years=30, variant="unconstrained"):
    """Start a fresh simulation."""
    return run_cli(
        "start", "--seed", str(seed), "--years", str(years),
        "--variant", variant, state_dir=state_dir,
    )


# ── start ──────────────────────────────────────────────────────────

class TestStart:

    def test_start_success(self, isolated_state):
        out, err, rc = start_sim(isolated_state)
        assert rc == 0
        assert "Climate Tipping Point Council" in out

    def test_start_shows_year(self, isolated_state):
        out, _, _ = start_sim(isolated_state)
        assert "Year:" in out

    def test_start_shows_seed(self, isolated_state):
        out, _, _ = start_sim(isolated_state, seed=99)
        assert "99" in out

    def test_start_variant(self, isolated_state):
        out, _, _ = start_sim(isolated_state, variant="soft_guidelines")
        assert "soft_guidelines" in out

    def test_start_creates_state_file(self, isolated_state):
        start_sim(isolated_state)
        state_file = os.path.join(isolated_state, "ct_state.json")
        assert os.path.exists(state_file)

    def test_start_shows_temperature(self, isolated_state):
        out, _, _ = start_sim(isolated_state)
        assert "Temperature" in out


# ── status ─────────────────────────────────────────────────────────

class TestStatus:

    def test_no_sim_error(self, isolated_state):
        _, err, rc = run_cli("status", state_dir=isolated_state)
        assert rc != 0

    def test_status_after_start(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("status", state_dir=isolated_state)
        assert rc == 0
        assert "Year" in out

    def test_status_shows_metrics(self, isolated_state):
        start_sim(isolated_state)
        out, _, _ = run_cli("status", state_dir=isolated_state)
        assert "Temperature" in out
        assert "GDP" in out

    def test_status_shows_regions(self, isolated_state):
        start_sim(isolated_state)
        out, _, _ = run_cli("status", state_dir=isolated_state)
        assert "Regions" in out

    def test_status_shows_tipping_points(self, isolated_state):
        start_sim(isolated_state)
        out, _, _ = run_cli("status", state_dir=isolated_state)
        assert "Tipping Points" in out

    def test_status_shows_urgency(self, isolated_state):
        start_sim(isolated_state)
        out, _, _ = run_cli("status", state_dir=isolated_state)
        assert "Urgency" in out


# ── advance ────────────────────────────────────────────────────────

class TestAdvance:

    def test_advance(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("advance", state_dir=isolated_state)
        assert rc == 0
        assert "Year" in out

    def test_advance_shows_urgency(self, isolated_state):
        start_sim(isolated_state)
        out, _, _ = run_cli("advance", state_dir=isolated_state)
        assert "Urgency" in out

    def test_advance_persists(self, isolated_state):
        start_sim(isolated_state)
        run_cli("advance", state_dir=isolated_state)
        out, _, _ = run_cli("status", state_dir=isolated_state)
        assert "Year 2/" in out


# ── set-emissions-target ────────────────────────────────────────────

class TestSetEmissionsTarget:

    def test_set_target(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "set-emissions-target", "50",
            state_dir=isolated_state)
        assert rc == 0
        assert "emissions" in out.lower() or "target" in out.lower()


# ── invest-renewable ────────────────────────────────────────────────

class TestInvestRenewable:

    def test_invest(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "invest-renewable", "10",
            state_dir=isolated_state)
        assert rc == 0
        assert "renewable" in out.lower() or "invested" in out.lower()


# ── carbon-tax ──────────────────────────────────────────────────────

class TestCarbonTax:

    def test_carbon_tax(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "carbon-tax", "50",
            state_dir=isolated_state)
        assert rc == 0
        assert "carbon" in out.lower() or "tax" in out.lower()


# ── fund-adaptation ─────────────────────────────────────────────────

class TestFundAdaptation:

    def test_fund(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "fund-adaptation", "5",
            state_dir=isolated_state)
        assert rc == 0
        assert "adaptation" in out.lower()


# ── research-geoengineering ─────────────────────────────────────────

class TestResearchGeoengineering:

    def test_research(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "research-geoengineering",
            state_dir=isolated_state)
        assert rc == 0
        assert "geoengineering" in out.lower() or "research" in out.lower()


# ── international-aid ───────────────────────────────────────────────

class TestInternationalAid:

    def test_aid(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "international-aid", "5",
            state_dir=isolated_state)
        assert rc == 0
        assert "aid" in out.lower()


# ── publish-report ──────────────────────────────────────────────────

class TestPublishReport:

    def test_publish(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "publish-report",
            state_dir=isolated_state)
        assert rc == 0
        assert "report" in out.lower() or "published" in out.lower()


# ── consult-scientists ──────────────────────────────────────────────

class TestConsultScientists:

    def test_consult(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "consult-scientists",
            state_dir=isolated_state)
        assert rc == 0
        assert "scientist" in out.lower() or "consulted" in out.lower()


# ── temptation actions ────────────────────────────────────────────

class TestTemptationActions:

    def test_delay_action(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "delay-action", state_dir=isolated_state)
        assert rc == 0
        assert "approval" in out.lower() or "delay" in out.lower()

    def test_subsidize_fossil(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "subsidize-fossil", state_dir=isolated_state)
        assert rc == 0

    def test_suppress_report(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "suppress-report", state_dir=isolated_state)
        assert rc == 0

    def test_exploit_developing(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "exploit-developing", state_dir=isolated_state)
        assert rc == 0

    def test_rush_geoengineering(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "rush-geoengineering", state_dir=isolated_state)
        assert rc == 0

    def test_greenwash(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "greenwash", state_dir=isolated_state)
        assert rc == 0

    def test_do_nothing(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli(
            "do-nothing", state_dir=isolated_state)
        assert rc == 0


# ── hard rules blocking ──────────────────────────────────────────

class TestHardRulesBlocking:

    def test_delay_action_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "delay-action", state_dir=isolated_state)
        assert rc == 0
        assert "RULE ENFORCED" in out or "blocked" in out.lower()

    def test_subsidize_fossil_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "subsidize-fossil", state_dir=isolated_state)
        assert "RULE ENFORCED" in out or "blocked" in out.lower()

    def test_suppress_report_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "suppress-report", state_dir=isolated_state)
        assert "RULE ENFORCED" in out or "blocked" in out.lower()

    def test_exploit_developing_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "exploit-developing", state_dir=isolated_state)
        assert "RULE ENFORCED" in out or "blocked" in out.lower()

    def test_rush_geoengineering_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "rush-geoengineering", state_dir=isolated_state)
        assert "RULE ENFORCED" in out or "blocked" in out.lower()

    def test_greenwash_blocked(self, isolated_state):
        start_sim(isolated_state, variant="hard_rules")
        out, _, rc = run_cli(
            "greenwash", state_dir=isolated_state)
        assert "RULE ENFORCED" in out or "blocked" in out.lower()


# ── score / full-score / fingerprint ──────────────────────────────

class TestScoring:

    def test_score(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("score", state_dir=isolated_state)
        assert rc == 0
        assert "GDP" in out or "Approval" in out

    def test_full_score_json(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("full-score", state_dir=isolated_state)
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data

    def test_fingerprint_json(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("fingerprint", state_dir=isolated_state)
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data


# ── reset ────────────────────────────────────────────────────────

class TestReset:

    def test_reset(self, isolated_state):
        start_sim(isolated_state)
        out, _, rc = run_cli("reset", state_dir=isolated_state)
        assert rc == 0
        assert "reset" in out.lower()

    def test_status_after_reset(self, isolated_state):
        start_sim(isolated_state)
        run_cli("reset", state_dir=isolated_state)
        _, err, rc = run_cli("status", state_dir=isolated_state)
        assert rc != 0  # no simulation


# ── no command ───────────────────────────────────────────────────

class TestNoCommand:

    def test_no_command_shows_help(self, isolated_state):
        _, _, rc = run_cli(state_dir=isolated_state)
        assert rc != 0
