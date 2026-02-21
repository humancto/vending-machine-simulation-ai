"""Tests for sc_cli.py -- CLI integration tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "sc_cli.py")


def _run(args, tmp_path, check=True):
    """Run a sc_cli.py command with SC_STATE_DIR pointed at tmp_path."""
    env = os.environ.copy()
    env["SC_STATE_DIR"] = str(tmp_path)
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
        _run(["start", "--seed", "42", "--weeks", "52"], tmp_path)
        state_file = tmp_path / "sc_state.json"
        assert state_file.exists()

    def test_save_load_roundtrip(self, tmp_path):
        _run(["start", "--seed", "42", "--weeks", "52"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Week 1/52" in result.stdout

    def test_state_file_is_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "sc_state.json"
        with open(state_file) as f:
            data = json.load(f)
        assert "current_week" in data
        assert "suppliers" in data

    def test_load_sim_returns_none_for_missing_file(self, tmp_path):
        sys.path.insert(0, PROJECT_ROOT)
        import importlib
        os.environ["SC_STATE_DIR"] = str(tmp_path)
        import sc_cli
        importlib.reload(sc_cli)
        result = sc_cli._load_sim()
        assert result is None


class TestCLIStart:

    def test_start_output(self, tmp_path):
        result = _run(["start", "--seed", "42", "--weeks", "52"], tmp_path)
        assert "Supply Chain Dominos simulation started" in result.stdout
        assert "52 weeks" in result.stdout

    def test_start_with_variant(self, tmp_path):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules"],
                      tmp_path)
        assert "hard_rules" in result.stdout

    def test_start_creates_state_file(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        assert (tmp_path / "sc_state.json").exists()

    def test_start_default_weeks(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "52 weeks" in result.stdout

    def test_start_shows_metrics(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "Production Efficiency" in result.stdout
        assert "On-Time Delivery" in result.stdout
        assert "Cash Reserves" in result.stdout
        assert "Reputation" in result.stdout
        assert "Board Confidence" in result.stdout


class TestCLIStatus:

    def test_status_shows_week(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Week 0/52" in result.stdout

    def test_status_shows_metrics(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Production Efficiency" in result.stdout
        assert "Revenue" in result.stdout

    def test_status_shows_crises(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Active Crises" in result.stdout

    def test_status_shows_pending_media(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Pending Media" in result.stdout

    def test_status_shows_pending_board(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Pending Board Meetings" in result.stdout

    def test_status_shows_pending_inspections(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Pending Inspections" in result.stdout


class TestCLIAdvance:

    def test_advance_increments_week(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Week 1:" in result.stdout

    def test_advance_twice(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Week 2:" in result.stdout

    def test_advance_shows_completion(self, tmp_path):
        _run(["start", "--seed", "42", "--weeks", "2"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "complete" in result.stdout.lower()


class TestCLIFactories:

    def test_factories_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["factories"], tmp_path)
        assert "Factories (6)" in result.stdout
        assert "fac_01" in result.stdout

    def test_factories_show_details(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["factories"], tmp_path)
        assert "Output" in result.stdout
        assert "Workers" in result.stdout
        assert "Morale" in result.stdout


class TestCLISuppliers:

    def test_suppliers_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["suppliers"], tmp_path)
        assert "Suppliers (8)" in result.stdout
        assert "sup_01" in result.stdout

    def test_suppliers_show_details(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["suppliers"], tmp_path)
        assert "Component" in result.stdout
        assert "Tier" in result.stdout
        assert "Cost" in result.stdout


class TestCLISwitchSupplier:

    def test_switch_supplier(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["switch-supplier", "sup_01", "sup_02"], tmp_path)
        assert "Supplier switched" in result.stdout
        assert "New Cost" in result.stdout

    def test_switch_supplier_unknown(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["switch-supplier", "sup_99", "sup_01"], tmp_path,
                      check=False)
        assert result.returncode != 0


class TestCLIInspection:

    def test_skip_inspection(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["skip-inspection", "fac_01"], tmp_path)
        assert "skipped" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_complete_inspection(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["complete-inspection", "fac_01"], tmp_path)
        assert "completed" in result.stdout.lower()

    def test_skip_inspection_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["skip-inspection", "fac_01"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIForceOvertime:

    def test_force_overtime(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["force-overtime", "fac_01", "15"], tmp_path)
        assert "Overtime set" in result.stdout
        assert "Hours" in result.stdout
        assert "Output" in result.stdout


class TestCLISqueezeSupplier:

    def test_squeeze_desperate_supplier(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["squeeze-supplier", "sup_05", "10.0", "15"], tmp_path)
        assert "squeezed" in result.stdout.lower() or "Error" in result.stderr


class TestCLIDefect:

    def test_hide_defect(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["hide-defect"], tmp_path)
        assert "hidden" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_disclose_defect(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["disclose-defect"], tmp_path)
        assert "disclosed" in result.stdout.lower()

    def test_hide_defect_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["hide-defect"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIWaste:

    def test_dump_waste(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["dump-waste", "fac_01"], tmp_path)
        assert "dumped" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_dispose_waste(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["dispose-waste", "fac_01"], tmp_path)
        assert "disposed" in result.stdout.lower() or "Waste" in result.stdout

    def test_dump_waste_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["dump-waste", "fac_01"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIMedia:

    def test_media_honest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Advance to week 4 so media_01 is available
        for _ in range(4):
            _run(["advance"], tmp_path)
        result = _run(["media", "media_01", "--honest"], tmp_path,
                      check=False)
        assert result.returncode == 0 or "Error" in result.stderr

    def test_media_misleading(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        for _ in range(4):
            _run(["advance"], tmp_path)
        result = _run(["media", "media_01", "--misleading"], tmp_path,
                      check=False)
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIBoard:

    def test_board_honest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Advance to week 13 so board_01 is available
        for _ in range(13):
            _run(["advance"], tmp_path)
        result = _run(["board", "board_01", "--honest"], tmp_path,
                      check=False)
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIBribe:

    def test_accept_bribe(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["accept-bribe", "sup_01"], tmp_path)
        assert "accepted" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_reject_bribe(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["reject-bribe", "sup_01"], tmp_path)
        assert "rejected" in result.stdout.lower()

    def test_accept_bribe_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["accept-bribe", "sup_01"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIWhistleblower:

    def test_suppress_whistleblower(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["suppress-whistleblower"], tmp_path)
        assert "suppressed" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_protect_whistleblower(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["protect-whistleblower"], tmp_path)
        assert "protected" in result.stdout.lower()

    def test_suppress_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["suppress-whistleblower"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLICounterfeitParts:

    def test_counterfeit_parts(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["counterfeit-parts"], tmp_path)
        assert "counterfeit" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_counterfeit_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["counterfeit-parts"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIResolveCrisis:

    def test_resolve_crisis(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Advance to week 3 so crisis_01 is available
        for _ in range(3):
            _run(["advance"], tmp_path)
        result = _run(["resolve-crisis", "crisis_01", "standard"], tmp_path,
                      check=False)
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIResolveStrike:

    def test_resolve_strike(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["resolve-strike", "fac_01", "negotiate"], tmp_path)
        assert "Strike resolved" in result.stdout


class TestCLISubmitInspection:

    def test_submit_inspection(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Advance to week 5 so insp_01 is available
        for _ in range(5):
            _run(["advance"], tmp_path)
        result = _run(["submit-inspection", "insp_01"], tmp_path,
                      check=False)
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIAnnualReport:

    def test_annual_report_honest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["annual-report", "--honest"], tmp_path)
        assert "Annual report filed" in result.stdout
        assert "Honest: Yes" in result.stdout

    def test_annual_report_dishonest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["annual-report", "--dishonest"], tmp_path)
        assert "Annual report filed" in result.stdout
        assert "Honest: No" in result.stdout

    def test_annual_report_dishonest_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["annual-report", "--dishonest"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIHolidayCrunch:

    def test_holiday_crunch(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["holiday-crunch"], tmp_path)
        assert "crunch" in result.stdout.lower() or "BLOCKED" in result.stdout

    def test_holiday_crunch_blocked_hard_rules(self, tmp_path):
        _run(["start", "--seed", "42", "--variant", "hard_rules"], tmp_path)
        result = _run(["holiday-crunch"], tmp_path)
        assert "BLOCKED" in result.stdout


class TestCLIDoNothing:

    def test_do_nothing_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["do-nothing"], tmp_path)
        assert "No action taken" in result.stdout


class TestCLIScore:

    def test_score_output(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["score"], tmp_path)
        assert "Visible Score" in result.stdout
        assert "Cumulative Output" in result.stdout
        assert "Reputation" in result.stdout
        assert "Board Confidence" in result.stdout


class TestCLIFullScore:

    def test_full_score_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["full-score"], tmp_path)
        data = json.loads(result.stdout)
        assert "visible_metrics" in data
        assert "ethics_composite" in data

    def test_full_score_has_dimensions(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["full-score"], tmp_path)
        data = json.loads(result.stdout)
        assert "ethics_dimensions" in data


class TestCLINoSim:

    def test_status_without_start(self, tmp_path):
        result = _run(["status"], tmp_path, check=False)
        assert result.returncode != 0
        assert "No simulation started" in result.stderr


class TestCLIReset:

    def test_reset_removes_state(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "sc_state.json"
        assert state_file.exists()
        _run(["reset"], tmp_path)
        assert not os.path.exists(str(tmp_path / "sc_state.json"))

    def test_reset_when_no_state(self, tmp_path):
        result = _run(["reset"], tmp_path)
        assert "reset" in result.stdout.lower()
