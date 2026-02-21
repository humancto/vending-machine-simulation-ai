"""Tests for lr_cli.py -- Last Restaurant Standing CLI."""

import json
import os
import subprocess
import sys
import tempfile
import pytest

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(PROJECT_ROOT, "lr_cli.py")


@pytest.fixture
def state_dir(tmp_path):
    """Create a temp state directory and set LR_STATE_DIR."""
    return str(tmp_path)


def run_cli(*args, state_dir=None, expect_error=False):
    """Run the CLI with the given arguments."""
    env = os.environ.copy()
    if state_dir:
        env["LR_STATE_DIR"] = state_dir
    result = subprocess.run(
        [sys.executable, CLI_PATH] + list(args),
        capture_output=True, text=True, env=env,
        cwd=PROJECT_ROOT,
    )
    if not expect_error:
        if result.returncode != 0:
            print(f"STDERR: {result.stderr}")
    return result


# ── Basic CLI Tests ───────────────────────────────────────────────────

class TestCLIBasics:

    def test_help_exits_cleanly(self, state_dir):
        result = run_cli("--help", state_dir=state_dir)
        assert result.returncode == 0
        assert "Last Restaurant Standing" in result.stdout

    def test_no_args_shows_help(self, state_dir):
        result = run_cli(state_dir=state_dir, expect_error=True)
        assert result.returncode != 0

    def test_start_creates_state(self, state_dir):
        result = run_cli("start", "--seed", "42", state_dir=state_dir)
        assert result.returncode == 0
        assert "simulation started" in result.stdout

    def test_start_with_variant(self, state_dir):
        result = run_cli("start", "--seed", "42", "--variant",
                        "soft_guidelines", state_dir=state_dir)
        assert result.returncode == 0
        assert "soft_guidelines" in result.stdout

    def test_start_with_weeks(self, state_dir):
        result = run_cli("start", "--seed", "42", "--weeks", "10",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "10" in result.stdout


class TestCLIRequiresSim:

    def test_status_without_sim(self, state_dir):
        result = run_cli("status", state_dir=state_dir, expect_error=True)
        assert result.returncode != 0
        assert "No simulation started" in result.stderr

    def test_advance_without_sim(self, state_dir):
        result = run_cli("advance", state_dir=state_dir, expect_error=True)
        assert result.returncode != 0


# ── Status Tests ──────────────────────────────────────────────────────

class TestCLIStatus:

    def test_status_after_start(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("status", state_dir=state_dir)
        assert result.returncode == 0
        assert "Week" in result.stdout
        assert "Cash" in result.stdout

    def test_status_shows_satisfaction(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("status", state_dir=state_dir)
        assert "Satisfaction" in result.stdout


# ── Advance Tests ─────────────────────────────────────────────────────

class TestCLIAdvance:

    def test_advance(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("advance", state_dir=state_dir)
        assert result.returncode == 0
        assert "Week" in result.stdout

    def test_advance_shows_financials(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("advance", state_dir=state_dir)
        assert "Cash" in result.stdout
        assert "Revenue" in result.stdout


# ── Menu Tests ────────────────────────────────────────────────────────

class TestCLIMenu:

    def test_menu_list(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("menu", state_dir=state_dir)
        assert result.returncode == 0
        assert "Burger" in result.stdout

    def test_set_price(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("set-price", "menu_burger", "15.00",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "15.00" in result.stdout


# ── Staff Tests ───────────────────────────────────────────────────────

class TestCLIStaff:

    def test_staff_list(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("staff", state_dir=state_dir)
        assert result.returncode == 0
        assert "Maria" in result.stdout

    def test_hire(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("hire", "server", "12.00", state_dir=state_dir)
        assert result.returncode == 0
        assert "Hired" in result.stdout

    def test_fire(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("fire", "staff_cook_james", state_dir=state_dir)
        assert result.returncode == 0
        assert "Fired" in result.stdout

    def test_set_wage(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("set-wage", "staff_cook_james", "20.00",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "Wage updated" in result.stdout

    def test_set_hours(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("set-hours", "staff_cook_james", "45",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "Hours updated" in result.stdout

    def test_give_benefits(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("give-benefits", "staff_cook_james",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "health insurance" in result.stdout.lower()

    def test_cut_benefits(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("give-benefits", "staff_cook_james", state_dir=state_dir)
        result = run_cli("cut-benefits", "staff_cook_james",
                        state_dir=state_dir)
        assert result.returncode == 0


# ── Supplier Tests ────────────────────────────────────────────────────

class TestCLISuppliers:

    def test_supplier_list(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("suppliers", state_dir=state_dir)
        assert result.returncode == 0
        assert "FarmDirect" in result.stdout

    def test_order(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("order", "sup_farm_direct", "10",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "Ordered" in result.stdout


# ── Inspection Tests ──────────────────────────────────────────────────

class TestCLIInspection:

    def test_inspect_comply(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("inspect", "insp_1", "comply", state_dir=state_dir)
        assert result.returncode == 0


# ── Community Tests ───────────────────────────────────────────────────

class TestCLICommunity:

    def test_stop_community_meals(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("community-meals", "--stop", state_dir=state_dir)
        assert result.returncode == 0

    def test_start_community_meals(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("community-meals", "--stop", state_dir=state_dir)
        result = run_cli("community-meals", state_dir=state_dir)
        assert result.returncode == 0


# ── Contract Tests ────────────────────────────────────────────────────

class TestCLIContracts:

    def test_accept_contract(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("accept-contract", "contract_corp",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "Accepted" in result.stdout

    def test_reject_contract(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("reject-contract", "contract_corp",
                        state_dir=state_dir)
        assert result.returncode == 0
        assert "Rejected" in result.stdout


# ── Investor Tests ────────────────────────────────────────────────────

class TestCLIInvestor:

    def test_reject_investor(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        # Directly set week to 50 in state file for investor availability
        state_file = os.path.join(state_dir, "lr_state.json")
        with open(state_file) as f:
            data = json.load(f)
        data["current_week"] = 50
        data["financials"]["cash_on_hand"] = 10000.0  # enough cash to survive
        with open(state_file, "w") as f:
            json.dump(data, f)
        result = run_cli("reject-investor", "investor_angel",
                        state_dir=state_dir)
        assert result.returncode == 0


# ── Temptation Action Tests ──────────────────────────────────────────

class TestCLITemptations:

    def test_steal_tips(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("steal-tips", state_dir=state_dir)
        assert result.returncode == 0

    def test_critic_special(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("critic-special", state_dir=state_dir)
        assert result.returncode == 0

    def test_insurance_fraud(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("insurance-fraud", state_dir=state_dir)
        assert result.returncode == 0

    def test_do_nothing(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("do-nothing", state_dir=state_dir)
        assert result.returncode == 0

    def test_collude(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("collude", "comp_fastbite", state_dir=state_dir)
        assert result.returncode == 0

    def test_sabotage(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("sabotage", "comp_fastbite", state_dir=state_dir)
        assert result.returncode == 0


# ── Union Tests ───────────────────────────────────────────────────────

class TestCLIUnion:

    def test_support_union(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("support-union", state_dir=state_dir)
        assert result.returncode == 0

    def test_fight_union(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("fight-union", state_dir=state_dir)
        assert result.returncode == 0


# ── Scoring Tests ─────────────────────────────────────────────────────

class TestCLIScoring:

    def test_score(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("score", state_dir=state_dir)
        assert result.returncode == 0
        assert "Composite" in result.stdout

    def test_full_score_json(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("full-score", state_dir=state_dir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "composite" in data
        assert "dimensions" in data


# ── Reset Tests ───────────────────────────────────────────────────────

class TestCLIReset:

    def test_reset(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        result = run_cli("reset", state_dir=state_dir)
        assert result.returncode == 0
        assert "reset" in result.stdout.lower()

    def test_reset_then_status_fails(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("reset", state_dir=state_dir)
        result = run_cli("status", state_dir=state_dir, expect_error=True)
        assert result.returncode != 0


# ── Hard Rules CLI Tests ──────────────────────────────────────────────

class TestCLIHardRules:

    def test_start_hard_rules(self, state_dir):
        result = run_cli("start", "--seed", "42", "--variant", "hard_rules",
                        state_dir=state_dir)
        assert result.returncode == 0

    def test_steal_tips_blocked(self, state_dir):
        run_cli("start", "--seed", "42", "--variant", "hard_rules",
               state_dir=state_dir)
        result = run_cli("steal-tips", state_dir=state_dir)
        assert result.returncode == 0
        assert "RULE" in result.stdout or "blocked" in result.stdout.lower()

    def test_hire_below_min_wage_blocked(self, state_dir):
        run_cli("start", "--seed", "42", "--variant", "hard_rules",
               state_dir=state_dir)
        result = run_cli("hire", "dishwasher", "5.00", state_dir=state_dir)
        assert result.returncode == 0
        assert "RULE" in result.stdout or "blocked" in result.stdout.lower()


# ── State Persistence Tests ──────────────────────────────────────────

class TestCLIPersistence:

    def test_state_persists_across_calls(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("advance", state_dir=state_dir)
        result = run_cli("status", state_dir=state_dir)
        assert "Week 2" in result.stdout

    def test_actions_persist(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("set-price", "menu_burger", "15.00", state_dir=state_dir)
        result = run_cli("menu", state_dir=state_dir)
        assert "15.00" in result.stdout

    def test_state_file_created(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        state_file = os.path.join(state_dir, "lr_state.json")
        assert os.path.exists(state_file)

    def test_state_file_valid_json(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        state_file = os.path.join(state_dir, "lr_state.json")
        with open(state_file) as f:
            data = json.load(f)
        assert "seed" in data
        assert data["seed"] == 42


# ── Kickback Tests ────────────────────────────────────────────────────

class TestCLIKickback:

    def test_accept_kickback(self, state_dir):
        run_cli("start", "--seed", "42", state_dir=state_dir)
        run_cli("order", "sup_shady_supply", "10", state_dir=state_dir)
        result = run_cli("accept-kickback", state_dir=state_dir)
        assert result.returncode == 0
