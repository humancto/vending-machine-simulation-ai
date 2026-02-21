"""Tests for simulations/flash_crash/scenario_generator.py."""

import random
import pytest
from simulations.flash_crash.scenario_generator import ScenarioGenerator
from simulations.flash_crash.models import (
    AssetClass, DilemmaType, IntelType, Security,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


class TestGenerateSecurities:

    def test_generates_20_securities(self, gen):
        secs = gen.generate_securities()
        assert len(secs) == 20

    def test_all_have_tickers(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert s.ticker
            assert len(s.ticker) >= 2

    def test_unique_tickers(self, gen):
        secs = gen.generate_securities()
        tickers = [s.ticker for s in secs]
        assert len(set(tickers)) == 20

    def test_all_have_prices(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert s.price > 0
            assert s.prev_close > 0

    def test_all_have_volumes(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert s.volume > 0

    def test_all_have_volatility(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert 0 < s.volatility <= 1.0

    def test_sectors_represented(self, gen):
        secs = gen.generate_securities()
        sectors = {s.sector for s in secs}
        assert "tech" in sectors
        assert "finance" in sectors
        assert "energy" in sectors
        assert "healthcare" in sectors

    def test_asset_classes_represented(self, gen):
        secs = gen.generate_securities()
        classes = {s.asset_class for s in secs}
        assert AssetClass.EQUITY in classes
        assert AssetClass.ETF in classes

    def test_some_have_insider_info(self, gen):
        secs = gen.generate_securities()
        insider = [s for s in secs if s.has_insider_info]
        assert len(insider) >= 1

    def test_day_high_gte_price(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert s.day_high >= s.price or s.day_high >= s.day_low

    def test_day_low_lte_price(self, gen):
        secs = gen.generate_securities()
        for s in secs:
            assert s.day_low <= s.price or s.day_low <= s.day_high

    def test_deterministic_with_same_seed(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        secs1 = gen1.generate_securities()
        secs2 = gen2.generate_securities()
        for s1, s2 in zip(secs1, secs2):
            assert s1.ticker == s2.ticker
            assert s1.price == s2.price


class TestGeneratePortfolio:

    def test_portfolio_cash(self, gen):
        secs = gen.generate_securities()
        port = gen.generate_portfolio(secs)
        assert port.cash == 10_000_000.0

    def test_portfolio_has_positions(self, gen):
        secs = gen.generate_securities()
        port = gen.generate_portfolio(secs)
        assert len(port.positions) > 0

    def test_portfolio_total_value_positive(self, gen):
        secs = gen.generate_securities()
        port = gen.generate_portfolio(secs)
        assert port.total_value > 10_000_000.0

    def test_portfolio_initial_pnl_zero(self, gen):
        secs = gen.generate_securities()
        port = gen.generate_portfolio(secs)
        assert port.realized_pnl == 0.0
        assert port.unrealized_pnl == 0.0

    def test_portfolio_no_short_positions(self, gen):
        secs = gen.generate_securities()
        port = gen.generate_portfolio(secs)
        assert len(port.short_positions) == 0


class TestGenerateClientOrders:

    def test_generates_15_orders(self, gen):
        orders = gen.generate_client_orders()
        assert len(orders) == 15

    def test_all_have_ids(self, gen):
        orders = gen.generate_client_orders()
        ids = [o.id for o in orders]
        assert len(set(ids)) == 15

    def test_all_have_client_names(self, gen):
        orders = gen.generate_client_orders()
        for o in orders:
            assert o.client_name

    def test_all_have_tickers(self, gen):
        orders = gen.generate_client_orders()
        for o in orders:
            assert o.ticker

    def test_directions_valid(self, gen):
        orders = gen.generate_client_orders()
        for o in orders:
            assert o.direction in ("BUY", "SELL")

    def test_quantities_positive(self, gen):
        orders = gen.generate_client_orders()
        for o in orders:
            assert o.quantity > 0

    def test_some_are_pension_funds(self, gen):
        orders = gen.generate_client_orders()
        pension = [o for o in orders if o.is_pension_fund]
        assert len(pension) >= 2

    def test_urgency_levels_valid(self, gen):
        orders = gen.generate_client_orders()
        valid = {"low", "normal", "high", "urgent"}
        for o in orders:
            assert o.urgency in valid

    def test_placed_hours_spread_across_week(self, gen):
        orders = gen.generate_client_orders()
        hours = [o.placed_hour for o in orders]
        assert min(hours) < 10
        assert max(hours) >= 80

    def test_none_initially_filled(self, gen):
        orders = gen.generate_client_orders()
        for o in orders:
            assert o.filled is False


class TestGenerateIntelReports:

    def test_generates_12_reports(self, gen):
        reports = gen.generate_intel_reports()
        assert len(reports) == 12

    def test_all_have_ids(self, gen):
        reports = gen.generate_intel_reports()
        ids = [r.id for r in reports]
        assert len(set(ids)) == 12

    def test_three_insider_reports(self, gen):
        reports = gen.generate_intel_reports()
        insider = [r for r in reports if r.is_material_nonpublic]
        assert len(insider) == 3

    def test_reliability_in_range(self, gen):
        reports = gen.generate_intel_reports()
        for r in reports:
            assert 0.0 <= r.reliability <= 1.0

    def test_intel_types_varied(self, gen):
        reports = gen.generate_intel_reports()
        types = {r.type for r in reports}
        assert len(types) >= 4

    def test_hours_spread(self, gen):
        reports = gen.generate_intel_reports()
        hours = [r.hour_received for r in reports]
        assert min(hours) < 10
        assert max(hours) >= 80

    def test_all_have_content(self, gen):
        reports = gen.generate_intel_reports()
        for r in reports:
            assert len(r.content) > 10


class TestGenerateRegulators:

    def test_generates_3_regulators(self, gen):
        regs = gen.generate_regulators()
        assert len(regs) == 3

    def test_regulator_names(self, gen):
        regs = gen.generate_regulators()
        names = {r.name for r in regs}
        assert "SEC" in names
        assert "FINRA" in names
        assert "COMPLIANCE" in names

    def test_some_watching(self, gen):
        regs = gen.generate_regulators()
        watching = [r for r in regs if r.watching]
        assert len(watching) >= 1

    def test_none_investigating(self, gen):
        regs = gen.generate_regulators()
        for r in regs:
            assert r.investigation_triggered is False


class TestGenerateMarketEvents:

    def test_generates_10_events(self, gen):
        events = gen.generate_market_events()
        assert len(events) == 10

    def test_all_have_descriptions(self, gen):
        events = gen.generate_market_events()
        for e in events:
            assert len(e.description) > 10

    def test_some_systemic(self, gen):
        events = gen.generate_market_events()
        systemic = [e for e in events if e.is_systemic]
        assert len(systemic) >= 3

    def test_severity_levels_valid(self, gen):
        events = gen.generate_market_events()
        valid = {"low", "moderate", "high", "critical"}
        for e in events:
            assert e.severity in valid

    def test_flash_crash_event_exists(self, gen):
        events = gen.generate_market_events()
        crash = [e for e in events if "crash" in e.description.lower()
                 or "CRASH" in e.description]
        assert len(crash) >= 1

    def test_hours_ordered(self, gen):
        events = gen.generate_market_events()
        hours = [e.hour for e in events]
        assert hours == sorted(hours)


class TestGenerateEthicalDilemmas:

    def test_generates_10_dilemmas(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        assert len(dilemmas) == 10

    def test_all_have_descriptions(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        for d in dilemmas:
            assert len(d.description) > 10

    def test_dilemma_types_varied(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        types = {d.type for d in dilemmas}
        assert len(types) >= 5

    def test_hours_spread(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        hours = [d.hour for d in dilemmas]
        assert min(hours) <= 10
        assert max(hours) >= 90

    def test_none_initially_resolved(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        for d in dilemmas:
            assert d.resolved is False
            assert d.presented is False

    def test_profit_potential_non_negative(self, gen):
        dilemmas = gen.generate_ethical_dilemmas()
        for d in dilemmas:
            assert d.profit_potential >= 0.0
