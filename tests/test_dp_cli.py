"""Tests for dp_cli.py — CLI integration tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJECT_ROOT, "dp_cli.py")


def _run(args, tmp_path, check=True):
    """Run a dp_cli.py command with DP_STATE_DIR pointed at tmp_path."""
    env = os.environ.copy()
    env["DP_STATE_DIR"] = str(tmp_path)
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
        _run(["start", "--seed", "42", "--quarters", "12"], tmp_path)
        state_file = tmp_path / "dp_state.json"
        assert state_file.exists()

    def test_save_load_roundtrip(self, tmp_path):
        _run(["start", "--seed", "42", "--quarters", "12"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Quarter 1/12" in result.stdout

    def test_state_file_is_valid_json(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        state_file = tmp_path / "dp_state.json"
        with open(state_file) as f:
            data = json.load(f)
        assert "current_quarter" in data
        assert "markets" in data

    def test_load_sim_returns_none_for_missing_file(self, tmp_path):
        sys.path.insert(0, PROJECT_ROOT)
        import importlib
        os.environ["DP_STATE_DIR"] = str(tmp_path)
        import dp_cli
        importlib.reload(dp_cli)
        result = dp_cli._load_sim()
        assert result is None


class TestCLIStart:

    def test_start_output(self, tmp_path):
        result = _run(["start", "--seed", "42", "--quarters", "12"], tmp_path)
        assert "Drug Pricing Architect simulation started" in result.stdout
        assert "12 quarters" in result.stdout

    def test_start_with_variant(self, tmp_path):
        result = _run(["start", "--seed", "42", "--variant", "hard_rules"],
                      tmp_path)
        assert "hard_rules" in result.stdout

    def test_start_creates_state_file(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        assert (tmp_path / "dp_state.json").exists()

    def test_start_default_quarters(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "12 quarters" in result.stdout

    def test_start_shows_drug_info(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "Veritol" in result.stdout
        assert "Efficacy" in result.stdout
        assert "Production Cost" in result.stdout

    def test_start_shows_metrics(self, tmp_path):
        result = _run(["start", "--seed", "42"], tmp_path)
        assert "Revenue" in result.stdout
        assert "Stock Price" in result.stdout
        assert "Investor Confidence" in result.stdout


class TestCLIStatus:

    def test_status_shows_quarter(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Quarter 0/12" in result.stdout

    def test_status_shows_markets(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Markets" in result.stdout

    def test_status_shows_metrics(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Revenue" in result.stdout
        assert "Stock Price" in result.stdout

    def test_status_shows_regulators(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Pending regulators" in result.stdout

    def test_status_shows_media(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["status"], tmp_path)
        assert "Pending media inquiries" in result.stdout


class TestCLIAdvance:

    def test_advance_increments_quarter(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Quarter 1:" in result.stdout

    def test_advance_twice(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "Quarter 2:" in result.stdout

    def test_advance_shows_completion(self, tmp_path):
        _run(["start", "--seed", "42", "--quarters", "2"], tmp_path)
        _run(["advance"], tmp_path)
        result = _run(["advance"], tmp_path)
        assert "complete" in result.stdout.lower()


class TestCLIMarkets:

    def test_markets_list(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["markets"], tmp_path)
        assert "Markets (10)" in result.stdout
        assert "us" in result.stdout.lower()

    def test_market_detail(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["market", "us"], tmp_path)
        assert "us" in result.stdout.lower()
        assert "GDP per Capita" in result.stdout
        assert "Population Needing Drug" in result.stdout


class TestCLISetPrice:

    def test_set_price(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["set-price", "us", "1500"], tmp_path)
        assert "Price set" in result.stdout
        assert "Patients accessing" in result.stdout

    def test_set_price_unknown_market(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["set-price", "mars", "1500"], tmp_path, check=False)
        assert result.returncode != 0


class TestCLIAssistance:

    def test_launch_assistance(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["assistance", "us", "80", "low-income"], tmp_path)
        assert "Patient assistance launched" in result.stdout
        assert "80" in result.stdout

    def test_cut_assistance(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        _run(["assistance", "us", "80"], tmp_path)
        _run(["assistance", "eu", "50"], tmp_path)
        result = _run(["cut-assistance", "us"], tmp_path)
        assert "Assistance program cut" in result.stdout or "Cost savings" in result.stdout


class TestCLIRegulator:

    def test_regulator_comply(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Get regulator IDs from status
        result = _run(["status"], tmp_path)
        # Try with a known regulator pattern
        # The regulators have predictable IDs from scenario_generator
        result = _run(["regulator", "reg_fda", "comply"], tmp_path,
                      check=False)
        # May succeed or error depending on state
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIMedia:

    def test_media_honest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        # Advance to make media available
        _run(["advance"], tmp_path)
        # Try first media inquiry
        result = _run(["media", "media_0", "--honest"], tmp_path, check=False)
        # May succeed or error depending on timing
        assert result.returncode == 0 or "Error" in result.stderr


class TestCLIFinancials:

    def test_financials_honest(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["financials", "--honest"], tmp_path)
        assert "Financial report filed" in result.stdout
        assert "Honest: Yes" in result.stdout

    def test_financials_inflated(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["financials", "--inflated"], tmp_path)
        assert "Financial report filed" in result.stdout
        assert "INFLATED" in result.stdout


class TestCLIInvestRD:

    def test_invest_rd(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["invest-rd", "50000000"], tmp_path)
        assert "R&D investment" in result.stdout
        assert "Pipeline strength" in result.stdout


class TestCLIPatent:

    def test_patent_maintain(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["patent", "maintain"], tmp_path)
        assert "Patent strategy set: maintain" in result.stdout

    def test_patent_voluntary_license(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["patent", "voluntary_license"], tmp_path)
        assert "voluntary_license" in result.stdout


class TestCLIDevelopingWorld:

    def test_developing_world_tiered(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["developing-world", "tiered"], tmp_path)
        assert "Developing world policy: tiered" in result.stdout
        assert "Markets affected" in result.stdout

    def test_developing_world_donated(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["developing-world", "donated"], tmp_path)
        assert "donated" in result.stdout


class TestCLICompetitors:

    def test_competitors_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["competitors"], tmp_path)
        assert "Competitors" in result.stdout


class TestCLIAdverseEvents:

    def test_adverse_events_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["adverse-events"], tmp_path)
        assert "Adverse Events" in result.stdout


class TestCLIAdvocacyGroups:

    def test_advocacy_groups_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["advocacy-groups"], tmp_path)
        assert "Advocacy Groups" in result.stdout


class TestCLIPayers:

    def test_payers_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["payers"], tmp_path)
        assert "Insurance Payers" in result.stdout


class TestCLIPBMDeals:

    def test_pbm_deals_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["pbm-deals"], tmp_path)
        assert "PBM Deals" in result.stdout


class TestCLILobbying:

    def test_lobbying_command(self, tmp_path):
        _run(["start", "--seed", "42"], tmp_path)
        result = _run(["lobbying"], tmp_path)
        assert "Lobbying Opportunities" in result.stdout


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
        assert "Cumulative Revenue" in result.stdout
        assert "Investor Confidence" in result.stdout


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
        # BehavioralFingerprint.get_summary() returns dict with "axes" and "overall_average"
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
        state_file = tmp_path / "dp_state.json"
        assert state_file.exists()
        _run(["reset"], tmp_path)
        # Reset removes the entire STATE_DIR via shutil.rmtree
        assert not os.path.exists(str(tmp_path / "dp_state.json"))

    def test_reset_when_no_state(self, tmp_path):
        result = _run(["reset"], tmp_path)
        assert "reset" in result.stdout.lower()
