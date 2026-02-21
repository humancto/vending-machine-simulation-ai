"""Tests for ms_cli.py -- CLI integration tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "ms_cli.py")


def _run(args, tmp_path, check=True):
    """Run a ms_cli.py command with MS_STATE_DIR pointed at tmp_path."""
    env = os.environ.copy()
    env["MS_STATE_DIR"] = str(tmp_path)
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
        _run(["start", "--seed", "42", "--months", "24"], tmp_path)
        state_file = tmp_path / "ms_state.json"
        assert state_file.exists()

    def test_save_load_roundtrip(self, tmp_path):
        _run(["start", "--seed", "42", "--months", "24"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Month 1/24" in result.stdout

    def test_state_file_is_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "ms_state.json"
        with open(state_file) as f:
            data = json.load(f)
        assert "current_month" in data
        assert "variant" in data

    def test_load_sim_returns_none_for_missing_file(self, tmp_path):
        sys.path.insert(0, PROJECT_ROOT)
        import importlib
        os.environ["MS_STATE_DIR"] = str(tmp_path)
        import ms_cli
        importlib.reload(ms_cli)
        result = ms_cli._load_sim()
        assert result is None


class TestCLIStart:

    def test_start_output(self, tmp_path):
        result = _run(["start", "--seed", "42", "--months", "24"], tmp_path)
        assert "Mayor of Splitsville simulation started" in result.stdout
        assert "24 months" in result.stdout

    def test_start_with_variant(self, tmp_path):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules"],
                      tmp_path)
        assert "hard_rules" in result.stdout

    def test_start_creates_state_file(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        assert (tmp_path / "ms_state.json").exists()

    def test_start_default_months(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "24 months" in result.stdout

    def test_start_shows_city_info(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "Splitsville" in result.stdout
        assert "200,000" in result.stdout

    def test_start_shows_metrics(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "Tax Revenue" in result.stdout
        assert "Job Growth" in result.stdout
        assert "City Approval" in result.stdout


class TestCLIStatus:

    def test_status_shows_month(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Month 0/24" in result.stdout

    def test_status_shows_metrics(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Tax Revenue" in result.stdout
        assert "Approval" in result.stdout

    def test_status_shows_stakeholders(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Stakeholders" in result.stdout

    def test_status_shows_budget(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Budget Remaining" in result.stdout


class TestCLIAdvance:

    def test_advance_increments_month(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Month 1:" in result.stdout

    def test_advance_twice(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Month 2:" in result.stdout

    def test_advance_shows_completion(self, tmp_path):
        _run(["start", "--seed", "42", "--months", "2"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "complete" in result.stdout.lower()


class TestCLIDistricts:

    def test_districts_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["districts"], tmp_path)
        assert "Districts (8)" in result.stdout
        assert "downtown" in result.stdout.lower()


class TestCLIApprove:

    def test_approve_project(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        _run(["env-review", "proj_01", "thorough"], tmp_path)
        result = _run(["approve", "proj_01"], tmp_path)
        assert "Approved" in result.stdout
        assert "Jobs" in result.stdout

    def test_approve_unknown_project(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["approve", "proj_nonexistent"], tmp_path, check=False)
        assert result.returncode != 0


class TestCLIDeny:

    def test_deny_project(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["deny", "proj_01"], tmp_path)
        assert "Denied" in result.stdout


class TestCLIZoning:

    def test_set_zoning(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["zoning", "downtown", "high_density"], tmp_path)
        assert "high_density" in result.stdout

    def test_set_zoning_unknown_district(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["zoning", "narnia", "residential"], tmp_path,
                      check=False)
        assert result.returncode != 0


class TestCLIAffordable:

    def test_set_affordable(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["affordable", "20"], tmp_path)
        assert "20" in result.stdout


class TestCLIBudget:

    def test_allocate_budget(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["budget", "affordable_housing", "50000000"], tmp_path)
        assert "Budget allocated" in result.stdout
        assert "affordable_housing" in result.stdout

    def test_budget_unknown_category(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["budget", "fantasy", "10"], tmp_path, check=False)
        assert result.returncode != 0


class TestCLITaxIncentive:

    def test_tax_incentive(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["tax-incentive", "TechVista", "50", "10"], tmp_path)
        assert "TechVista" in result.stdout
        assert "50" in result.stdout


class TestCLIFundTransit:

    def test_fund_transit(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["fund-transit", "route_02"], tmp_path)
        assert "Transit funded" in result.stdout

    def test_fund_transit_unknown_route(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["fund-transit", "route_nonexistent"], tmp_path,
                      check=False)
        assert result.returncode != 0


class TestCLIHearing:

    def test_hearing(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["hearing", "TechVista campus impact"], tmp_path)
        assert "Community hearing held" in result.stdout
        assert "Attendees" in result.stdout


class TestCLIProtest:

    def test_protest_listen(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["protest", "listen"], tmp_path)
        assert "listen" in result.stdout

    def test_protest_suppress(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["protest", "suppress"], tmp_path)
        assert "suppress" in result.stdout


class TestCLIRentControl:

    def test_rent_control(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["rent-control", "riverside", "5"], tmp_path)
        assert "Rent control set" in result.stdout
        assert "Riverside" in result.stdout

    def test_rent_control_unknown_district(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["rent-control", "narnia", "5"], tmp_path,
                      check=False)
        assert result.returncode != 0


class TestCLIDisplacementAssist:

    def test_displacement_assist(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["displacement-assist", "5000000"], tmp_path)
        assert "Displacement assistance" in result.stdout


class TestCLIDonations:

    def test_accept_donation(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["accept-donation", "donation_01"], tmp_path)
        assert "Donation accepted" in result.stdout

    def test_reject_donation(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["reject-donation", "donation_01"], tmp_path)
        assert "Donation rejected" in result.stdout


class TestCLIFastTrack:

    def test_fast_track(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["fast-track", "proj_01"], tmp_path)
        assert "Fast-tracked" in result.stdout


class TestCLIEnvReview:

    def test_thorough_review(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["env-review", "proj_01", "thorough"], tmp_path)
        assert "thorough" in result.stdout

    def test_expedited_review(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["env-review", "proj_01", "expedited"], tmp_path)
        assert "expedited" in result.stdout


class TestCLIRelocate:

    def test_relocate(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["relocate", "riverside"], tmp_path)
        assert "relocated" in result.stdout.lower()


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
        assert "Tax Revenue" in result.stdout
        assert "City Approval" in result.stdout


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


class TestCLIFingerprint:

    def test_fingerprint_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["fingerprint"], tmp_path)
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "overall_average" in data or "axes" in data

    def test_fingerprint_has_axes(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["fingerprint"], tmp_path)
        data = json.loads(result.stdout)
        if "axes" in data:
            assert len(data["axes"]) == 12


class TestCLINoSim:

    def test_status_without_start(self, tmp_path):
        result = _run(["status"], tmp_path, check=False)
        assert result.returncode != 0
        assert "No simulation started" in result.stderr


class TestCLIReset:

    def test_reset_removes_state(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "ms_state.json"
        assert state_file.exists()
        _run(["reset"], tmp_path)
        assert not os.path.exists(str(tmp_path / "ms_state.json"))

    def test_reset_when_no_state(self, tmp_path):
        result = _run(["reset"], tmp_path)
        assert "reset" in result.stdout.lower()
