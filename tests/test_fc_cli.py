"""Tests for fc_cli.py — Flash Crash Trader CLI."""

import json
import os
import subprocess
import sys
import tempfile
import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SCRIPT_DIR, "fc_cli.py")


@pytest.fixture(autouse=True)
def tmp_state_dir(tmp_path):
    """Use a temp directory for each test's state file."""
    os.environ["FC_STATE_DIR"] = str(tmp_path)
    yield tmp_path
    os.environ.pop("FC_STATE_DIR", None)


def run_cli(*args, expect_error=False):
    """Run fc_cli.py with args and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, CLI, *args],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONPATH": SCRIPT_DIR},
    )
    if not expect_error and result.returncode != 0:
        # Allow printing stderr for debugging
        pass
    return result.stdout, result.stderr, result.returncode


class TestStart:

    def test_start_default(self):
        out, _, rc = run_cli("start")
        assert rc == 0
        assert "Flash Crash Trader simulation started" in out

    def test_start_with_seed(self):
        out, _, rc = run_cli("start", "--seed", "42")
        assert rc == 0
        assert "42" in out

    def test_start_with_hours(self):
        out, _, rc = run_cli("start", "--hours", "60")
        assert rc == 0
        assert "60" in out

    def test_start_with_variant(self):
        out, _, rc = run_cli("start", "--variant", "soft_guidelines")
        assert rc == 0
        assert "soft_guidelines" in out

    def test_start_hard_rules(self):
        out, _, rc = run_cli("start", "--variant", "hard_rules")
        assert rc == 0
        assert "hard_rules" in out

    def test_start_creates_state_file(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        state_file = os.path.join(str(tmp_state_dir), "fc_state.json")
        assert os.path.exists(state_file)


class TestStatus:

    def test_status_requires_start(self):
        _, _, rc = run_cli("status", expect_error=True)
        assert rc != 0

    def test_status_after_start(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Hour" in out
        assert "Portfolio Value" in out

    def test_status_shows_desk_ranking(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("status")
        assert "Desk Ranking" in out


class TestAdvance:

    def test_advance(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("advance")
        assert rc == 0
        assert "Hour" in out

    def test_advance_multiple(self):
        run_cli("start", "--seed", "42")
        for _ in range(5):
            out, _, rc = run_cli("advance")
            assert rc == 0


class TestPortfolio:

    def test_portfolio(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("portfolio")
        assert rc == 0
        assert "Total Value" in out
        assert "Cash" in out

    def test_positions_alias(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("positions")
        assert rc == 0


class TestSecurities:

    def test_securities(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("securities")
        assert rc == 0
        assert "NVX" in out
        assert "SPX" in out


class TestSecurity:

    def test_security_detail(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("security", "NVX")
        assert rc == 0
        assert "NVX" in out
        assert "Price" in out

    def test_security_unknown(self):
        run_cli("start", "--seed", "42")
        _, _, rc = run_cli("security", "FAKE", expect_error=True)
        assert rc != 0


class TestTrade:

    def test_buy_trade(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("trade", "QBT", "buy", "100")
        assert rc == 0
        assert "Trade executed" in out

    def test_sell_trade(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("trade", "NVX", "sell", "100")
        assert rc == 0


class TestFillClient:

    def test_fill_client(self):
        run_cli("start", "--seed", "42")
        # co_1 placed at hour 2, advance past it
        for _ in range(3):
            run_cli("advance")
        out, _, rc = run_cli("fill-client", "co_1")
        assert rc == 0
        assert "filled" in out.lower() or "Order" in out


class TestDelayClient:

    def test_delay_client(self):
        run_cli("start", "--seed", "42")
        # co_1 placed at hour 2, advance past it
        for _ in range(3):
            run_cli("advance")
        out, _, rc = run_cli("delay-client", "co_1")
        assert rc == 0


class TestShort:

    def test_short(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("short", "QBT", "100")
        assert rc == 0
        assert "Short sold" in out


class TestCover:

    def test_cover(self):
        run_cli("start", "--seed", "42")
        run_cli("short", "QBT", "100")
        out, _, rc = run_cli("cover", "QBT", "100")
        assert rc == 0


class TestIntel:

    def test_intel_list(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("intel")
        assert rc == 0
        assert "Intel" in out

    def test_review_intel(self):
        run_cli("start", "--seed", "42")
        # Advance to make intel available
        for _ in range(7):
            run_cli("advance")
        out, _, rc = run_cli("review-intel", "intel_2")
        assert rc == 0
        assert "Intel Report" in out


class TestTradeOnIntel:

    def test_trade_on_intel(self):
        run_cli("start", "--seed", "42")
        for _ in range(7):
            run_cli("advance")
        out, _, rc = run_cli("trade-on-intel", "intel_2", "PTX", "buy", "50")
        assert rc == 0


class TestSpoof:

    def test_spoof(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("spoof", "NVX", "buy", "5000")
        assert rc == 0


class TestWash:

    def test_wash(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("wash", "NVX", "1000")
        assert rc == 0


class TestChurn:

    def test_churn(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("churn", "co_1")
        assert rc == 0


class TestReport:

    def test_report(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("report", "suspicious activity spotted")
        assert rc == 0
        assert "compliance" in out.lower() or "Report" in out


class TestRespondRegulator:

    def test_comply(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("respond-regulator", "reg_sec", "comply")
        assert rc == 0

    def test_resist(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("respond-regulator", "reg_sec", "resist")
        assert rc == 0


class TestWarnClients:

    def test_warn(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("warn-clients", "Market is volatile")
        assert rc == 0


class TestHedge:

    def test_hedge_defensive(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("hedge", "defensive")
        assert rc == 0

    def test_hedge_aggressive(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("hedge", "aggressive")
        assert rc == 0


class TestLiquidate:

    def test_liquidate(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("liquidate", "NVX")
        assert rc == 0


class TestRiskLimits:

    def test_risk_limits(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("risk-limits", "500000", "5.0")
        assert rc == 0


class TestWhistleblow:

    def test_whistleblow(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("whistleblow")
        assert rc == 0
        assert "fraud" in out.lower() or "reported" in out.lower() or "SEC" in out


class TestConceal:

    def test_conceal(self):
        run_cli("start", "--seed", "42")
        run_cli("trade", "QBT", "buy", "100")
        out, _, rc = run_cli("conceal", "trade_1")
        assert rc == 0


class TestRedact:

    def test_redact(self):
        run_cli("start", "--seed", "42")
        run_cli("trade", "QBT", "buy", "100")
        out, _, rc = run_cli("redact", "trade_1")
        assert rc == 0


class TestClients:

    def test_clients(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("clients")
        assert rc == 0
        assert "Client" in out or "orders" in out.lower()

    def test_client_orders_alias(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("client-orders")
        assert rc == 0


class TestDoNothing:

    def test_do_nothing(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("do-nothing")
        assert rc == 0


class TestScore:

    def test_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("score")
        assert rc == 0
        assert "Portfolio Value" in out
        assert "Desk Ranking" in out

    def test_full_score(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("full-score")
        assert rc == 0
        data = json.loads(out)
        assert "composite" in data
        assert "dimensions" in data


class TestFingerprint:

    def test_fingerprint(self):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("fingerprint")
        assert rc == 0
        assert "Behavioral Fingerprint" in out
        assert "Overall Average" in out


class TestReset:

    def test_reset(self, tmp_state_dir):
        run_cli("start", "--seed", "42")
        out, _, rc = run_cli("reset")
        assert rc == 0
        assert "reset" in out.lower()
        state_file = os.path.join(str(tmp_state_dir), "fc_state.json")
        assert not os.path.exists(state_file)


class TestNoCommand:

    def test_no_command(self):
        _, _, rc = run_cli(expect_error=True)
        assert rc != 0


class TestStatePersistence:

    def test_state_persists_across_calls(self):
        run_cli("start", "--seed", "42")
        run_cli("advance")
        run_cli("advance")
        out, _, rc = run_cli("status")
        assert rc == 0
        assert "Hour 2" in out or "Hour  2" in out

    def test_trade_persists(self):
        run_cli("start", "--seed", "42")
        run_cli("trade", "QBT", "buy", "100")
        out, _, rc = run_cli("portfolio")
        assert rc == 0
        assert "QBT" in out
