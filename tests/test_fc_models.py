"""Tests for simulations/flash_crash/models.py — all data models."""

import pytest
from simulations.flash_crash.models import (
    AssetClass, ClientOrder, DilemmaType, EthicalDilemma, IntelReport,
    IntelType, MarketEvent, MarketPhase, OrderType, Portfolio, Regulator,
    Security, TradeRecord, TradingViolation,
)


class TestEnums:

    def test_market_phase_values(self):
        assert MarketPhase.PRE_MARKET.value == "pre_market"
        assert MarketPhase.OPEN.value == "open"
        assert MarketPhase.MIDDAY.value == "midday"
        assert MarketPhase.POWER_HOUR.value == "power_hour"
        assert MarketPhase.CLOSE.value == "close"
        assert MarketPhase.AFTER_HOURS.value == "after_hours"
        assert MarketPhase.WEEKEND.value == "weekend"

    def test_market_phase_count(self):
        assert len(MarketPhase) == 7

    def test_order_type_values(self):
        assert OrderType.MARKET.value == "market"
        assert OrderType.LIMIT.value == "limit"
        assert OrderType.STOP_LOSS.value == "stop_loss"
        assert OrderType.SHORT_SELL.value == "short_sell"
        assert OrderType.COVER_SHORT.value == "cover_short"
        assert OrderType.OPTIONS_CALL.value == "options_call"
        assert OrderType.OPTIONS_PUT.value == "options_put"

    def test_order_type_count(self):
        assert len(OrderType) == 7

    def test_asset_class_values(self):
        assert AssetClass.EQUITY.value == "equity"
        assert AssetClass.BOND.value == "bond"
        assert AssetClass.COMMODITY.value == "commodity"
        assert AssetClass.DERIVATIVE.value == "derivative"
        assert AssetClass.CRYPTO.value == "crypto"
        assert AssetClass.ETF.value == "etf"

    def test_asset_class_count(self):
        assert len(AssetClass) == 6

    def test_intel_type_values(self):
        assert IntelType.PUBLIC.value == "public"
        assert IntelType.RUMOR.value == "rumor"
        assert IntelType.INSIDER.value == "insider"
        assert IntelType.LEAK.value == "leak"
        assert IntelType.ANALYST_TIP.value == "analyst_tip"
        assert IntelType.DARK_POOL_FLOW.value == "dark_pool_flow"

    def test_intel_type_count(self):
        assert len(IntelType) == 6

    def test_trading_violation_values(self):
        assert TradingViolation.INSIDER_TRADING.value == "insider_trading"
        assert TradingViolation.FRONT_RUNNING.value == "front_running"
        assert TradingViolation.MARKET_MANIPULATION.value == "market_manipulation"
        assert TradingViolation.WASH_TRADING.value == "wash_trading"
        assert TradingViolation.SPOOFING.value == "spoofing"
        assert TradingViolation.LATE_REPORTING.value == "late_reporting"
        assert TradingViolation.CLIENT_CHURNING.value == "client_churning"

    def test_trading_violation_count(self):
        assert len(TradingViolation) == 7

    def test_dilemma_type_values(self):
        assert DilemmaType.INSIDER_TIP.value == "insider_tip"
        assert DilemmaType.CLIENT_FRONT_RUN.value == "client_front_run"
        assert DilemmaType.FLASH_CRASH_EXPLOIT.value == "flash_crash_exploit"
        assert DilemmaType.SPOOFING_OPPORTUNITY.value == "spoofing_opportunity"
        assert DilemmaType.WASH_TRADE.value == "wash_trade"
        assert DilemmaType.DARK_POOL_ABUSE.value == "dark_pool_abuse"
        assert DilemmaType.CLIENT_CHURNING.value == "client_churning"
        assert DilemmaType.WHISTLEBLOWER_DECISION.value == "whistleblower_decision"
        assert DilemmaType.SYSTEMIC_RISK_IGNORE.value == "systemic_risk_ignore"
        assert DilemmaType.CONFLICT_OF_INTEREST.value == "conflict_of_interest"
        assert DilemmaType.LATE_DISCLOSURE.value == "late_disclosure"
        assert DilemmaType.BAILOUT_ABUSE.value == "bailout_abuse"

    def test_dilemma_type_count(self):
        assert len(DilemmaType) == 12


class TestSecurity:

    def test_create_security(self):
        sec = Security(
            id="sec_test", ticker="TST", name="Test Corp",
            sector="tech", asset_class=AssetClass.EQUITY,
            price=100.0, prev_close=98.0, day_high=102.0,
            day_low=97.0, volume=1000000, volatility=0.25,
        )
        assert sec.ticker == "TST"
        assert sec.price == 100.0
        assert sec.has_insider_info is False

    def test_security_with_insider_info(self):
        sec = Security(
            id="sec_ins", ticker="INS", name="Insider Corp",
            sector="finance", asset_class=AssetClass.EQUITY,
            price=50.0, prev_close=49.0, day_high=51.0,
            day_low=48.0, volume=500000, volatility=0.20,
            has_insider_info=True,
        )
        assert sec.has_insider_info is True

    def test_security_to_dict(self):
        sec = Security(
            id="sec_test", ticker="TST", name="Test Corp",
            sector="tech", asset_class=AssetClass.EQUITY,
            price=100.0, prev_close=98.0, day_high=102.0,
            day_low=97.0, volume=1000000, volatility=0.25,
        )
        d = sec.to_dict()
        assert d["ticker"] == "TST"
        assert d["price"] == 100.0
        assert d["asset_class"] == "equity"
        assert d["has_insider_info"] is False

    def test_security_from_dict(self):
        d = {
            "id": "sec_test", "ticker": "TST", "name": "Test Corp",
            "sector": "tech", "asset_class": "equity",
            "price": 100.0, "prev_close": 98.0, "day_high": 102.0,
            "day_low": 97.0, "volume": 1000000, "volatility": 0.25,
        }
        sec = Security.from_dict(d)
        assert sec.ticker == "TST"
        assert sec.asset_class == AssetClass.EQUITY
        assert sec.has_insider_info is False

    def test_security_roundtrip(self):
        sec = Security(
            id="sec_rt", ticker="RT", name="Roundtrip",
            sector="finance", asset_class=AssetClass.BOND,
            price=95.0, prev_close=94.0, day_high=96.0,
            day_low=93.0, volume=200000, volatility=0.10,
            has_insider_info=True,
        )
        restored = Security.from_dict(sec.to_dict())
        assert restored.ticker == sec.ticker
        assert restored.price == sec.price
        assert restored.has_insider_info == sec.has_insider_info
        assert restored.asset_class == sec.asset_class


class TestPortfolio:

    def test_default_portfolio(self):
        p = Portfolio()
        assert p.cash == 10_000_000.0
        assert p.total_value == 15_000_000.0
        assert p.realized_pnl == 0.0
        assert p.unrealized_pnl == 0.0
        assert p.positions == {}
        assert p.short_positions == {}

    def test_portfolio_with_positions(self):
        p = Portfolio(
            positions={"NVX": 100, "SPX": 200},
            cash=5_000_000.0,
        )
        assert p.positions["NVX"] == 100
        assert p.positions["SPX"] == 200
        assert p.cash == 5_000_000.0

    def test_portfolio_to_dict(self):
        p = Portfolio(
            positions={"NVX": 100},
            short_positions={"SPX": 50},
            cash=8_000_000.0,
            realized_pnl=50000.0,
        )
        d = p.to_dict()
        assert d["positions"]["NVX"] == 100
        assert d["short_positions"]["SPX"] == 50
        assert d["cash"] == 8_000_000.0
        assert d["realized_pnl"] == 50000.0

    def test_portfolio_from_dict(self):
        d = {
            "positions": {"NVX": 100},
            "short_positions": {},
            "cash": 9_000_000.0,
            "total_value": 12_000_000.0,
            "unrealized_pnl": 500.0,
            "realized_pnl": 1000.0,
        }
        p = Portfolio.from_dict(d)
        assert p.positions["NVX"] == 100
        assert p.cash == 9_000_000.0
        assert p.realized_pnl == 1000.0

    def test_portfolio_roundtrip(self):
        p = Portfolio(
            positions={"A": 10, "B": 20},
            short_positions={"C": 5},
            cash=7_000_000.0,
            total_value=11_000_000.0,
            unrealized_pnl=-500.0,
            realized_pnl=3000.0,
        )
        restored = Portfolio.from_dict(p.to_dict())
        assert restored.positions == p.positions
        assert restored.short_positions == p.short_positions
        assert restored.cash == p.cash


class TestClientOrder:

    def test_create_client_order(self):
        o = ClientOrder(
            id="co_1", client_name="Test Fund",
            ticker="NVX", direction="BUY", quantity=1000,
        )
        assert o.id == "co_1"
        assert o.filled is False
        assert o.is_pension_fund is False

    def test_pension_fund_order(self):
        o = ClientOrder(
            id="co_2", client_name="Pension Trust",
            ticker="SPX", direction="SELL", quantity=5000,
            is_pension_fund=True, urgency="urgent",
        )
        assert o.is_pension_fund is True
        assert o.urgency == "urgent"

    def test_client_order_to_dict(self):
        o = ClientOrder(
            id="co_1", client_name="Test",
            ticker="NVX", direction="BUY", quantity=100,
            placed_hour=5, urgency="high",
        )
        d = o.to_dict()
        assert d["id"] == "co_1"
        assert d["direction"] == "BUY"
        assert d["placed_hour"] == 5

    def test_client_order_from_dict(self):
        d = {
            "id": "co_1", "client_name": "Test",
            "ticker": "NVX", "direction": "BUY", "quantity": 100,
        }
        o = ClientOrder.from_dict(d)
        assert o.id == "co_1"
        assert o.filled is False

    def test_client_order_roundtrip(self):
        o = ClientOrder(
            id="co_rt", client_name="RT Fund",
            ticker="BPX", direction="SELL", quantity=500,
            limit_price=150.0, urgency="urgent",
            placed_hour=10, filled=True, fill_price=148.0,
            fill_hour=12, is_pension_fund=True,
        )
        restored = ClientOrder.from_dict(o.to_dict())
        assert restored.id == o.id
        assert restored.filled == o.filled
        assert restored.fill_price == o.fill_price
        assert restored.is_pension_fund == o.is_pension_fund


class TestIntelReport:

    def test_create_intel_report(self):
        r = IntelReport(
            id="intel_1", type=IntelType.PUBLIC,
            source="Bloomberg", content="Market update",
            ticker_mentioned="SPX", reliability=0.9,
            hour_received=5,
        )
        assert r.type == IntelType.PUBLIC
        assert r.is_material_nonpublic is False

    def test_insider_intel(self):
        r = IntelReport(
            id="intel_2", type=IntelType.INSIDER,
            source="CEO email", content="Earnings data",
            ticker_mentioned="ARC", reliability=0.95,
            hour_received=4, is_material_nonpublic=True,
        )
        assert r.is_material_nonpublic is True
        assert r.type == IntelType.INSIDER

    def test_intel_to_dict(self):
        r = IntelReport(
            id="intel_1", type=IntelType.LEAK,
            source="anon", content="info",
            ticker_mentioned="NVX", reliability=0.5,
            hour_received=10, is_material_nonpublic=True,
        )
        d = r.to_dict()
        assert d["type"] == "leak"
        assert d["is_material_nonpublic"] is True

    def test_intel_from_dict(self):
        d = {
            "id": "intel_1", "type": "public",
            "source": "Reuters", "content": "News",
            "ticker_mentioned": "SPX", "reliability": 0.8,
            "hour_received": 5,
        }
        r = IntelReport.from_dict(d)
        assert r.type == IntelType.PUBLIC
        assert r.is_material_nonpublic is False

    def test_intel_roundtrip(self):
        r = IntelReport(
            id="intel_rt", type=IntelType.DARK_POOL_FLOW,
            source="DP data", content="Large blocks",
            ticker_mentioned="BPX", reliability=0.6,
            hour_received=20, is_material_nonpublic=False,
        )
        restored = IntelReport.from_dict(r.to_dict())
        assert restored.type == r.type
        assert restored.reliability == r.reliability


class TestRegulator:

    def test_create_regulator(self):
        r = Regulator(id="reg_sec", name="SEC")
        assert r.watching is False
        assert r.investigation_triggered is False
        assert r.warnings_issued == 0

    def test_regulator_watching(self):
        r = Regulator(id="reg_finra", name="FINRA", watching=True)
        assert r.watching is True

    def test_regulator_to_dict(self):
        r = Regulator(
            id="reg_sec", name="SEC",
            watching=True, warnings_issued=2,
        )
        d = r.to_dict()
        assert d["name"] == "SEC"
        assert d["watching"] is True

    def test_regulator_from_dict(self):
        d = {"id": "reg_sec", "name": "SEC", "watching": True,
             "investigation_triggered": False, "warnings_issued": 1}
        r = Regulator.from_dict(d)
        assert r.name == "SEC"
        assert r.warnings_issued == 1

    def test_regulator_roundtrip(self):
        r = Regulator(
            id="reg_rt", name="FINRA",
            watching=True, investigation_triggered=True,
            warnings_issued=3,
        )
        restored = Regulator.from_dict(r.to_dict())
        assert restored.investigation_triggered == r.investigation_triggered
        assert restored.warnings_issued == r.warnings_issued


class TestMarketEvent:

    def test_create_market_event(self):
        e = MarketEvent(
            id="me_1", hour=50,
            description="Flash crash begins",
            affected_tickers=["SPX", "NVX"],
            severity="critical", is_systemic=True,
        )
        assert e.severity == "critical"
        assert e.is_systemic is True

    def test_market_event_to_dict(self):
        e = MarketEvent(
            id="me_1", hour=50,
            description="Event",
            affected_tickers=["SPX"],
        )
        d = e.to_dict()
        assert d["hour"] == 50
        assert "SPX" in d["affected_tickers"]

    def test_market_event_from_dict(self):
        d = {
            "id": "me_1", "hour": 50,
            "description": "Event",
            "affected_tickers": ["SPX"],
            "severity": "high",
            "is_systemic": True,
        }
        e = MarketEvent.from_dict(d)
        assert e.is_systemic is True

    def test_market_event_roundtrip(self):
        e = MarketEvent(
            id="me_rt", hour=75,
            description="Recovery",
            affected_tickers=["SPX", "NVX", "MGB"],
            severity="high", is_systemic=True,
        )
        restored = MarketEvent.from_dict(e.to_dict())
        assert restored.affected_tickers == e.affected_tickers


class TestEthicalDilemma:

    def test_create_dilemma(self):
        d = EthicalDilemma(
            id="dilemma_1", type=DilemmaType.INSIDER_TIP,
            description="Insider tip received",
            hour=4, temptation_action="trade_on_insider",
            profit_potential=500000.0,
        )
        assert d.profit_potential == 500000.0
        assert d.resolved is False
        assert d.presented is False

    def test_dilemma_to_dict(self):
        d = EthicalDilemma(
            id="dilemma_1", type=DilemmaType.SPOOFING_OPPORTUNITY,
            description="Spoof opportunity",
            hour=75, temptation_action="spoof_orders",
            profit_potential=400000.0,
        )
        dd = d.to_dict()
        assert dd["type"] == "spoofing_opportunity"
        assert dd["profit_potential"] == 400000.0

    def test_dilemma_from_dict(self):
        dd = {
            "id": "dilemma_1", "type": "insider_tip",
            "description": "Test", "hour": 4,
            "temptation_action": "trade", "profit_potential": 100000.0,
            "presented": True, "resolved": False, "resolution": None,
        }
        d = EthicalDilemma.from_dict(dd)
        assert d.type == DilemmaType.INSIDER_TIP
        assert d.presented is True

    def test_dilemma_roundtrip(self):
        d = EthicalDilemma(
            id="d_rt", type=DilemmaType.CLIENT_CHURNING,
            description="Churn opp",
            hour=55, temptation_action="churn",
            profit_potential=150000.0,
            presented=True, resolved=True,
            resolution="ignored",
        )
        restored = EthicalDilemma.from_dict(d.to_dict())
        assert restored.resolved == d.resolved
        assert restored.resolution == d.resolution


class TestTradeRecord:

    def test_create_trade_record(self):
        t = TradeRecord(
            id="trade_1", hour=10,
            ticker="NVX", direction="BUY",
            quantity=100, price=342.50,
            order_type="market",
        )
        assert t.direction == "BUY"
        assert t.concealed is False
        assert t.based_on_insider is False
        assert t.is_spoof is False
        assert t.is_wash is False

    def test_trade_record_to_dict(self):
        t = TradeRecord(
            id="trade_1", hour=10,
            ticker="NVX", direction="BUY",
            quantity=100, price=342.50,
            order_type="market",
            based_on_insider=True,
        )
        d = t.to_dict()
        assert d["based_on_insider"] is True
        assert d["ticker"] == "NVX"

    def test_trade_record_from_dict(self):
        d = {
            "id": "trade_1", "hour": 10,
            "ticker": "NVX", "direction": "BUY",
            "quantity": 100, "price": 342.50,
            "order_type": "market",
        }
        t = TradeRecord.from_dict(d)
        assert t.ticker == "NVX"
        assert t.concealed is False

    def test_trade_record_roundtrip(self):
        t = TradeRecord(
            id="t_rt", hour=50,
            ticker="SPX", direction="SHORT",
            quantity=5000, price=400.0,
            order_type="short_sell",
            is_spoof=True, concealed=True,
        )
        restored = TradeRecord.from_dict(t.to_dict())
        assert restored.is_spoof == t.is_spoof
        assert restored.concealed == t.concealed

    def test_trade_record_client_order(self):
        t = TradeRecord(
            id="trade_c", hour=15,
            ticker="NVX", direction="BUY",
            quantity=1000, price=345.0,
            order_type="market",
            is_client_order=True,
            client_order_id="co_1",
        )
        assert t.is_client_order is True
        assert t.client_order_id == "co_1"
