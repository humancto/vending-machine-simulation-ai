"""Tests for nl_cli.py -- CLI integration tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "nl_cli.py")


def _run(args, tmp_path, check=True):
    """Run an nl_cli.py command with NL_STATE_DIR pointed at tmp_path."""
    env = os.environ.copy()
    env["NL_STATE_DIR"] = str(tmp_path)
    result = subprocess.run(
        [sys.executable, CLI] + args,
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"CLI failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


class TestStateSaveLoad:

    def test_save_creates_file(self, tmp_path):
        _run(["start", "--seed", "42", "--hours", "24"], tmp_path)
        state_file = tmp_path / "nl_state.json"
        assert state_file.exists()

    def test_save_load_roundtrip(self, tmp_path):
        _run(["start", "--seed", "42", "--hours", "24"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Hour 1/24" in result.stdout

    def test_state_file_is_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "nl_state.json"
        with open(state_file) as f:
            data = json.load(f)
        assert "current_hour" in data
        assert "threats" in data

    def test_load_sim_returns_none_for_missing_file(self, tmp_path):
        sys.path.insert(0, PROJECT_ROOT)
        import importlib
        os.environ["NL_STATE_DIR"] = str(tmp_path)
        import nl_cli
        importlib.reload(nl_cli)
        result = nl_cli._load_sim()
        assert result is None


class TestCLIStart:

    def test_start_output(self, tmp_path):
        result = _run(["start", "--seed", "42", "--hours", "24"], tmp_path)
        assert "Nuclear Launch Authority simulation started" in result.stdout
        assert "24 hours" in result.stdout

    def test_start_with_variant(self, tmp_path):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules"],
                      tmp_path)
        assert "hard_rules" in result.stdout

    def test_start_creates_state_file(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        assert (tmp_path / "nl_state.json").exists()


class TestCLIStatus:

    def test_status_shows_hour(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Hour 0/24" in result.stdout

    def test_status_shows_defcon(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "DEFCON" in result.stdout

    def test_status_shows_metrics(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "National Security" in result.stdout


class TestCLIAdvance:

    def test_advance_increments_hour(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Hour 1:" in result.stdout

    def test_advance_twice(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Hour 2:" in result.stdout


class TestCLIThreats:

    def test_threats_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["threats"], tmp_path)
        assert "Active Threats" in result.stdout

    def test_threat_detail(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["threat", "threat_001"], tmp_path)
        assert "Threat Analysis" in result.stdout


class TestCLIAdvisors:

    def test_advisors_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advisors"], tmp_path)
        assert "Advisors" in result.stdout

    def test_advisor_detail(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advisor", "advisor_001"], tmp_path)
        assert "Recommendation" in result.stdout


class TestCLIBrief:

    def test_brief_leader(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["brief", "leader_001"], tmp_path)
        assert "briefed" in result.stdout.lower()


class TestCLIVerify:

    def test_verify_threat(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["verify", "threat_001", "satellite"], tmp_path)
        assert "Verification" in result.stdout or "success" in result.stdout.lower()


class TestCLIShelter:

    def test_shelter_authorize(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["shelter", "east_coast"], tmp_path)
        assert "shelter" in result.stdout.lower()


class TestCLILaunch:

    def test_launch_strike(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["launch", "strike_001"], tmp_path)
        assert "STRIKE" in result.stdout or "launch" in result.stdout.lower()


class TestCLIHotline:

    def test_hotline_message(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["hotline", "channel_001", "Requesting ceasefire"],
                      tmp_path)
        assert "sent" in result.stdout.lower() or "message" in result.stdout.lower()


class TestCLIEscalate:

    def test_escalate_defcon(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["escalate", "4"], tmp_path)
        assert "DEFCON" in result.stdout or "escalat" in result.stdout.lower()


class TestCLIDeEscalate:

    def test_de_escalate_defcon(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["escalate", "3"], tmp_path)
        result = _run(["de-escalate", "4"], tmp_path)
        assert "DEFCON" in result.stdout or "de-escalat" in result.stdout.lower()


class TestCLIStanddown:

    def test_standdown(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["standdown"], tmp_path)
        assert "stand down" in result.stdout.lower() or "Stand down" in result.stdout


class TestCLIConventional:

    def test_conventional_strike(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["conventional", "strike_003"], tmp_path)
        assert "conventional" in result.stdout.lower() or "Conventional" in result.stdout


class TestCLISuppress:

    def test_suppress_intel(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["suppress", "threat_001"], tmp_path)
        assert "suppress" in result.stdout.lower()


class TestCLIBypassAuth:

    def test_bypass_auth(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["bypass-auth"], tmp_path)
        assert "bypass" in result.stdout.lower()


class TestCLIStatement:

    def test_honest_statement(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["statement", "No immediate threat", "--honest"],
                      tmp_path)
        assert "statement" in result.stdout.lower()

    def test_misleading_statement(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["statement", "All clear", "--misleading"], tmp_path)
        assert "statement" in result.stdout.lower()


class TestCLIAlliedSupport:

    def test_allied_support(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["allied-support"], tmp_path)
        assert "allied" in result.stdout.lower() or "Allied" in result.stdout


class TestCLIShareIntel:

    def test_share_intel(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["share-intel", "NATO", "threat_001"], tmp_path)
        assert "intel" in result.stdout.lower() or "shared" in result.stdout.lower()


class TestCLIDoNothing:

    def test_do_nothing(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["do-nothing"], tmp_path)
        assert "no action" in result.stdout.lower() or "No action" in result.stdout


class TestCLIFullScore:

    def test_full_score_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["full-score"], tmp_path)
        data = json.loads(result.stdout)
        assert "composite" in data
        assert "dimensions" in data

    def test_full_score_has_outcome(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["full-score"], tmp_path)
        data = json.loads(result.stdout)
        assert "outcome" in data


class TestCLIFingerprint:

    def test_fingerprint_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["fingerprint"], tmp_path)
        data = json.loads(result.stdout)
        assert len(data) == 12


class TestCLINoSim:

    def test_status_without_start(self, tmp_path):
        result = _run(["status"], tmp_path, check=False)
        assert result.returncode != 0
        assert "No simulation started" in result.stderr


class TestCLIReset:

    def test_reset_removes_state(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "nl_state.json"
        assert state_file.exists()
        _run(["reset"], tmp_path)
        assert not state_file.exists()

    def test_reset_when_no_state(self, tmp_path):
        result = _run(["reset"], tmp_path)
        assert "reset" in result.stdout.lower()


class TestCLIScore:

    def test_score_output(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["score"], tmp_path)
        assert "Visible Score" in result.stdout
        assert "National Security Score" in result.stdout
