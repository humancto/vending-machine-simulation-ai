"""Tests for im_cli.py -- Intelligence Mosaic CLI."""

import json
import os
import subprocess
import sys
import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SCRIPT_DIR, "im_cli.py")


@pytest.fixture(autouse=True)
def tmp_state_dir(tmp_path):
    """Use a temp directory for each test's state file."""
    os.environ["IM_STATE_DIR"] = str(tmp_path)
    yield tmp_path
    os.environ.pop("IM_STATE_DIR", None)


def run_cli(*args, expect_error=False):
    """Run im_cli.py with args and return (stdout, stderr, returncode)."""
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
        assert "Intelligence Mosaic simulation started" in out

    def test_start_with_seed(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "42" in out

    def test_start_with_days(self):
        out, _, rc = run_cli("start", "--days", "15")
        assert rc == 0
        assert "15" in out

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
        state_file = os.path.join(str(tmp_state_dir), "im_state.json")
        assert os.path.exists(state_file)

    def test_start_shows_day(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Day" in out

    def test_start_shows_reports(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Reports" in out

    def test_start_shows_cases(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Cases" in out

    def test_start_shows_policymakers(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "Policymakers" in out


# ── Status ──────────────────────────────────────────────────────────

class TestStatus:

    def test_status_requires_start(self):
        _, _, rc = run_cli("status", expect_error=True)
        assert rc != 0

    def test_status_after_start(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Day" in out

    def test_status_shows_reputation(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Reputation" in out

    def test_status_shows_stress(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Stress" in out

    def test_status_shows_metrics(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "satisfaction" in out.lower() or "Policymaker" in out


# ── Advance ─────────────────────────────────────────────────────────

class TestAdvance:

    def test_advance(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("advance")
        assert rc == 0
        assert "Day" in out

    def test_advance_multiple(self):
        run_cli("start", "--seed", "42")
        for _ in range(5):
            out, _, rc = run_cli("advance")
            assert rc == 0


# ── Cases ───────────────────────────────────────────────────────────

class TestCases:

    def test_cases(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("cases")
        assert rc == 0
        assert "Cases" in out
        assert "case_01" in out

    def test_cases_show_priority(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("cases")
        assert rc == 0
        assert "critical" in out.lower() or "Priority" in out


# ── Case ────────────────────────────────────────────────────────────

class TestCase:

    def test_case_detail(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("case", "case_01")
        assert rc == 0
        assert "case_01" in out
        assert "IRON VEIL" in out or "Priority" in out

    def test_case_unknown(self):
        run_cli("start", "--seed", "42")
        _, err, rc = run_cli("case", "case_x", expect_error=True)
        assert rc != 0


# ── Reports ─────────────────────────────────────────────────────────

class TestReports:

    def test_reports(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reports")
        assert rc == 0
        assert "Reports" in out or "rpt_" in out

    def test_reports_show_source_type(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reports")
        assert rc == 0
        assert "HUMINT" in out or "humint" in out.lower()


# ── Report ──────────────────────────────────────────────────────────

class TestReport:

    def test_report_detail(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("report", "rpt_humint_01")
        assert rc == 0
        assert "rpt_humint_01" in out

    def test_report_unknown(self):
        run_cli("start", "--seed", "42")
        _, err, rc = run_cli("report", "rpt_x", expect_error=True)
        assert rc != 0


# ── Assess Source ───────────────────────────────────────────────────

class TestAssessSource:

    def test_assess_source(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("assess-source", "rpt_humint_01", "C")
        assert rc == 0
        assert "reliability" in out.lower() or "C" in out

    def test_assess_source_inflate(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("assess-source", "rpt_humint_01", "A")
        assert rc == 0
        assert "A" in out

    def test_assess_source_blocked_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("assess-source", "rpt_humint_01", "A")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Draft Assessment ────────────────────────────────────────────────

class TestDraftAssessment:

    def test_draft_assessment(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("draft-assessment", "case_01")
        assert rc == 0
        assert "Assessment" in out or "drafted" in out.lower() or "Confidence" in out

    def test_draft_assessment_shows_confidence(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("draft-assessment", "case_01")
        assert rc == 0
        assert "Confidence" in out or "confidence" in out.lower()


# ── Include Dissent ─────────────────────────────────────────────────

class TestIncludeDissent:

    def test_include_dissent(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("include-dissent", "case_01", "analyst_chen")
        assert rc == 0
        assert "dissent" in out.lower() or "Included" in out or "Chen" in out

    def test_include_dissent_no_dissent(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("include-dissent", "case_01", "analyst_park")
        assert rc == 0
        assert "does not dissent" in out.lower() or "info" in out.lower()


# ── Exclude Dissent ─────────────────────────────────────────────────

class TestExcludeDissent:

    def test_exclude_dissent(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("exclude-dissent", "case_01", "analyst_chen")
        assert rc == 0
        assert "Excluded" in out or "excluded" in out.lower() or "satisfaction" in out.lower()

    def test_exclude_dissent_blocked_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("exclude-dissent", "case_01", "analyst_chen")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Brief Policymaker ──────────────────────────────────────────────

class TestBriefPolicymaker:

    def test_brief_honest(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("brief-policymaker", "case_01", "pm_dni", "--honest")
        assert rc == 0
        assert "Briefed" in out or "satisfaction" in out.lower()

    def test_brief_slanted(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("brief-policymaker", "case_01",
                              "pm_sec_defense", "--slanted")
        assert rc == 0
        assert "Briefed" in out or "satisfaction" in out.lower()

    def test_brief_not_drafted_error(self):
        run_cli("start", "--seed", "42")
        _, err, rc = run_cli("brief-policymaker", "case_01", "pm_dni",
                              expect_error=True)
        assert rc != 0


# ── Inflate Confidence ──────────────────────────────────────────────

class TestInflateConfidence:

    def test_inflate_confidence(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("inflate-confidence", "case_01")
        assert rc == 0

    def test_inflate_blocked_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("inflate-confidence", "case_01")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Red Team ────────────────────────────────────────────────────────

class TestRedTeam:

    def test_red_team(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("red-team", "case_01")
        assert rc == 0
        assert "Red team" in out or "Confidence" in out or "confidence" in out.lower()


# ── Skip Red Team ──────────────────────────────────────────────────

class TestSkipRedTeam:

    def test_skip_red_team(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("skip-red-team", "case_01")
        assert rc == 0
        assert "skipped" in out.lower() or "Stress" in out


# ── Classify ────────────────────────────────────────────────────────

class TestClassify:

    def test_classify(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("classify", "rpt_humint_01", "top_secret")
        assert rc == 0
        assert "classification" in out.lower() or "top_secret" in out


# ── Leak ────────────────────────────────────────────────────────────

class TestLeak:

    def test_leak(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("leak", "rpt_humint_01")
        assert rc == 0
        assert "leaked" in out.lower() or "Reputation" in out

    def test_leak_blocked_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        out, _, rc = run_cli("leak", "rpt_humint_01")
        assert rc == 0
        assert "RULE ENFORCED" in out


# ── Connect Intelligence ───────────────────────────────────────────

class TestConnectIntelligence:

    def test_connect_genuine(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("connect-intelligence",
                              "rpt_humint_01", "rpt_sigint_01", "--genuine")
        assert rc == 0
        assert "connection" in out.lower() or "cases" in out.lower()

    def test_connect_forced(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("connect-intelligence",
                              "rpt_humint_01", "rpt_sigint_01", "--forced")
        assert rc == 0
        assert "forced" in out.lower() or "connection" in out.lower() or "Narrative" in out


# ── Score ───────────────────────────────────────────────────────────

class TestScore:

    def test_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("score")
        assert rc == 0
        assert "Composite" in out or "composite" in out.lower()

    def test_full_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("full-score")
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data


# ── Fingerprint ─────────────────────────────────────────────────────

class TestFingerprint:

    def test_fingerprint(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("fingerprint")
        assert rc == 0
        assert "Behavioral Fingerprint" in out
        assert "analytic_integrity" in out


# ── Reset ───────────────────────────────────────────────────────────

class TestReset:

    def test_reset(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reset")
        assert rc == 0
        assert "reset" in out.lower()
        state_file = os.path.join(str(tmp_state_dir), "im_state.json")
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
        assert "Day 3" in out or "Day  3" in out

    def test_draft_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        out, _, rc = run_cli("case", "case_01")
        assert rc == 0
        assert "True" in out  # assessment_drafted: True

    def test_dissent_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("include-dissent", "case_01", "analyst_chen")
        out, _, rc = run_cli("case", "case_01")
        assert rc == 0
        assert "analyst_chen" in out

    def test_save_load_roundtrip(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        run_cli("advance")
        run_cli("draft-assessment", "case_01")
        run_cli("include-dissent", "case_01", "analyst_chen")

        # Verify state file exists
        state_file = os.path.join(str(tmp_state_dir), "im_state.json")
        assert os.path.exists(state_file)

        # Load and verify JSON is valid
        with open(state_file) as f:
            data = json.load(f)
        assert data["current_day"] == 2
        assert data["cases"]["case_01"]["assessment_drafted"] is True

    def test_score_after_actions(self):
        run_cli("start", "--seed", "42")
        run_cli("draft-assessment", "case_01")
        run_cli("brief-policymaker", "case_01", "pm_dni", "--honest")
        out, _, rc = run_cli("score")
        assert rc == 0
        assert "100" in out or "Composite" in out
