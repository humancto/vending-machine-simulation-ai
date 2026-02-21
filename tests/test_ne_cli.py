"""Tests for ne_cli.py — News Editor Under Fire CLI."""

import json
import os
import subprocess
import sys
import tempfile

import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "ne_cli.py")
PYTHON = sys.executable


@pytest.fixture(autouse=True)
def isolated_state(tmp_path):
    """Ensure each test gets its own state directory."""
    state_dir = str(tmp_path / "ne_state")
    os.environ["NE_STATE_DIR"] = state_dir
    yield state_dir
    os.environ.pop("NE_STATE_DIR", None)


def run_cli(*args, expect_fail=False):
    """Run the CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [PYTHON, CLI] + list(args),
        capture_output=True,
        text=True,
        env={**os.environ},
        timeout=30,
    )
    if not expect_fail:
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
    return result.returncode, result.stdout, result.stderr


# ── Start Command ──────────────────────────────────────────────────────

class TestStartCommand:

    def test_start_default(self):
        code, out, err = run_cli("start", "--seed", "42")
        assert "simulation started" in out.lower()

    def test_start_with_hours(self):
        code, out, err = run_cli("start", "--hours", "24", "--seed", "42")
        assert "Duration: 24" in out

    def test_start_with_variant(self):
        code, out, err = run_cli("start", "--seed", "42", "--variant", "soft_guidelines")
        assert "soft_guidelines" in out

    def test_start_hard_rules(self):
        code, out, err = run_cli("start", "--seed", "42", "--variant", "hard_rules")
        assert "hard_rules" in out


# ── Status Command ─────────────────────────────────────────────────────

class TestStatusCommand:

    def test_status_requires_start(self):
        code, out, err = run_cli("status", expect_fail=True)
        assert code != 0

    def test_status_after_start(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("status")
        assert "Hour" in out
        assert "Readership" in out

    def test_status_shows_revenue(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("status")
        assert "Revenue" in out


# ── Advance Command ────────────────────────────────────────────────────

class TestAdvanceCommand:

    def test_advance(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("advance")
        assert "Hour" in out

    def test_advance_multiple(self):
        run_cli("start", "--seed", "42")
        for _ in range(5):
            code, out, err = run_cli("advance")
        assert "Hour" in out


# ── Stories Command ────────────────────────────────────────────────────

class TestStoriesCommand:

    def test_stories_list(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("stories")
        assert "Stories" in out
        assert "story_main_scandal" in out

    def test_story_detail(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("story", "story_main_scandal")
        # Should output JSON
        data = json.loads(out)
        assert data["id"] == "story_main_scandal"


# ── Sources Command ────────────────────────────────────────────────────

class TestSourcesCommand:

    def test_sources_list(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("sources")
        assert "Sources" in out
        assert "src_whistleblower" in out

    def test_source_detail(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("source", "src_whistleblower")
        data = json.loads(out)
        assert data["name"] == "Sarah Park"


# ── Reporters Command ──────────────────────────────────────────────────

class TestReportersCommand:

    def test_reporters_list(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("reporters")
        assert "Reporters" in out
        assert "rep_chen_li" in out

    def test_reporter_detail(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("reporter", "rep_chen_li")
        data = json.loads(out)
        assert data["name"] == "Chen Li"


# ── Assign Command ─────────────────────────────────────────────────────

class TestAssignCommand:

    def test_assign(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("assign", "rep_chen_li", "story_main_scandal")
        assert "Assigned" in out


# ── Publish Command ────────────────────────────────────────────────────

class TestPublishCommand:

    def test_publish(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("publish", "story_main_scandal")
        assert "Published" in out

    def test_publish_hard_rules_blocked(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        code, out, err = run_cli("publish", "story_main_scandal")
        assert "RULE" in out or "fact-check" in out.lower()


# ── Kill Command ───────────────────────────────────────────────────────

class TestKillCommand:

    def test_kill(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("kill", "story_affair_rumor")
        assert "Killed" in out


# ── Retract Command ────────────────────────────────────────────────────

class TestRetractCommand:

    def test_retract(self):
        run_cli("start", "--seed", "42")
        run_cli("publish", "story_main_scandal")
        code, out, err = run_cli("retract", "story_main_scandal")
        assert "Retracted" in out


# ── Fact-Check Command ─────────────────────────────────────────────────

class TestFactCheckCommand:

    def test_fact_check(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("fact-check", "story_main_scandal")
        assert "Verified" in out or "accuracy" in out.lower()


# ── Verify Command ─────────────────────────────────────────────────────

class TestVerifyCommand:

    def test_verify(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("verify", "src_whistleblower")
        assert "verified" in out.lower()


# ── Protect Command ────────────────────────────────────────────────────

class TestProtectCommand:

    def test_protect(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("protect", "src_whistleblower")
        assert "protection" in out.lower()


# ── Reveal Command ─────────────────────────────────────────────────────

class TestRevealCommand:

    def test_reveal(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("reveal", "src_whistleblower")
        assert "Revealed" in out

    def test_reveal_blocked_hard_rules(self):
        run_cli("start", "--seed", "42", "--variant", "hard_rules")
        code, out, err = run_cli("reveal", "src_whistleblower")
        assert "RULE" in out


# ── Sensationalize Command ─────────────────────────────────────────────

class TestSensationalizeCommand:

    def test_sensationalize(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("sensationalize", "story_main_scandal")
        assert "Sensationalized" in out


# ── Interview Command ──────────────────────────────────────────────────

class TestInterviewCommand:

    def test_interview(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("interview", "src_anonymous_tipster")
        assert "Interviewed" in out or "Reliability" in out


# ── Pressure Command ───────────────────────────────────────────────────

class TestPressureCommand:

    def test_pressure_list(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("pressure")
        assert "Pressures" in out


# ── Break Command ──────────────────────────────────────────────────────

class TestBreakCommand:

    def test_break(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("break", "rep_chen_li", "4")
        assert "resting" in out.lower() or "Fatigue" in out


# ── Push Deadline Command ──────────────────────────────────────────────

class TestPushDeadlineCommand:

    def test_push(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("push-deadline", "rep_chen_li")
        assert "Pushed" in out or "Fatigue" in out


# ── Meeting Command ────────────────────────────────────────────────────

class TestMeetingCommand:

    def test_meeting(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("meeting")
        assert "meeting" in out.lower()


# ── Correction Command ─────────────────────────────────────────────────

class TestCorrectionCommand:

    def test_correction(self):
        run_cli("start", "--seed", "42")
        run_cli("publish", "story_main_scandal")
        code, out, err = run_cli("correction", "story_main_scandal", "Fixed typo")
        assert "Correction" in out


# ── Statement Command ──────────────────────────────────────────────────

class TestStatementCommand:

    def test_statement(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("statement", "We stand by our reporting")
        assert "statement" in out.lower()


# ── Do Nothing Command ─────────────────────────────────────────────────

class TestDoNothingCommand:

    def test_do_nothing(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("do-nothing")
        assert "action" in out.lower() or "ticking" in out.lower()


# ── Score Commands ─────────────────────────────────────────────────────

class TestScoreCommands:

    def test_score(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("score")
        assert "Composite" in out

    def test_full_score(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("full-score")
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data

    def test_fingerprint(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("fingerprint")
        assert "Fingerprint" in out


# ── Reset Command ──────────────────────────────────────────────────────

class TestResetCommand:

    def test_reset(self):
        run_cli("start", "--seed", "42")
        code, out, err = run_cli("reset")
        assert "reset" in out.lower()

    def test_status_after_reset(self):
        run_cli("start", "--seed", "42")
        run_cli("reset")
        code, out, err = run_cli("status", expect_fail=True)
        assert code != 0


# ── No Command ─────────────────────────────────────────────────────────

class TestNoCommand:

    def test_no_command_shows_help(self):
        code, out, err = run_cli(expect_fail=True)
        assert code != 0


# ── State Persistence ──────────────────────────────────────────────────

class TestStatePersistence:

    def test_state_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("advance")
        run_cli("publish", "story_main_scandal")
        code, out, err = run_cli("status")
        assert "Hour 1" in out
        # Story should be published
        code, out2, err2 = run_cli("stories")
        assert "published" in out2.lower()
