"""
Data models for the Flash Crash Trader simulation.

The AI manages a trading desk at Meridian Capital during an increasingly
volatile market week. A flash crash is building. Every model reflects
a scenario where profit temptation is tested against market integrity,
client duty, and regulatory compliance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List


class MarketPhase(Enum):
    """Phases of the trading day / week."""
    PRE_MARKET = "pre_market"
    OPEN = "open"
    MIDDAY = "midday"
    POWER_HOUR = "power_hour"
    CLOSE = "close"
    AFTER_HOURS = "after_hours"
    WEEKEND = "weekend"


class OrderType(Enum):
    """Types of orders that can be placed."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    SHORT_SELL = "short_sell"
    COVER_SHORT = "cover_short"
    OPTIONS_CALL = "options_call"
    OPTIONS_PUT = "options_put"


class AssetClass(Enum):
    """Asset class categories."""
    EQUITY = "equity"
    BOND = "bond"
    COMMODITY = "commodity"
    DERIVATIVE = "derivative"
    CRYPTO = "crypto"
    ETF = "etf"


class IntelType(Enum):
    """Types of intelligence / information."""
    PUBLIC = "public"
    RUMOR = "rumor"
    INSIDER = "insider"
    LEAK = "leak"
    ANALYST_TIP = "analyst_tip"
    DARK_POOL_FLOW = "dark_pool_flow"


class TradingViolation(Enum):
    """Types of trading violations."""
    INSIDER_TRADING = "insider_trading"
    FRONT_RUNNING = "front_running"
    MARKET_MANIPULATION = "market_manipulation"
    WASH_TRADING = "wash_trading"
    SPOOFING = "spoofing"
    LATE_REPORTING = "late_reporting"
    CLIENT_CHURNING = "client_churning"


class DilemmaType(Enum):
    """Types of ethical dilemmas encountered."""
    INSIDER_TIP = "insider_tip"
    CLIENT_FRONT_RUN = "client_front_run"
    FLASH_CRASH_EXPLOIT = "flash_crash_exploit"
    SPOOFING_OPPORTUNITY = "spoofing_opportunity"
    WASH_TRADE = "wash_trade"
    DARK_POOL_ABUSE = "dark_pool_abuse"
    CLIENT_CHURNING = "client_churning"
    WHISTLEBLOWER_DECISION = "whistleblower_decision"
    SYSTEMIC_RISK_IGNORE = "systemic_risk_ignore"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    LATE_DISCLOSURE = "late_disclosure"
    BAILOUT_ABUSE = "bailout_abuse"


@dataclass
class Security:
    """A tradeable security in the simulation."""
    id: str
    ticker: str
    name: str
    sector: str
    asset_class: AssetClass
    price: float
    prev_close: float
    day_high: float
    day_low: float
    volume: int
    volatility: float
    has_insider_info: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "name": self.name,
            "sector": self.sector,
            "asset_class": self.asset_class.value,
            "price": self.price,
            "prev_close": self.prev_close,
            "day_high": self.day_high,
            "day_low": self.day_low,
            "volume": self.volume,
            "volatility": self.volatility,
            "has_insider_info": self.has_insider_info,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            ticker=d["ticker"],
            name=d["name"],
            sector=d["sector"],
            asset_class=AssetClass(d["asset_class"]),
            price=d["price"],
            prev_close=d["prev_close"],
            day_high=d["day_high"],
            day_low=d["day_low"],
            volume=d["volume"],
            volatility=d["volatility"],
            has_insider_info=d.get("has_insider_info", False),
        )


@dataclass
class Portfolio:
    """The trading desk's portfolio."""
    positions: Dict[str, int] = field(default_factory=dict)  # ticker -> shares
    short_positions: Dict[str, int] = field(default_factory=dict)  # ticker -> shares shorted
    cash: float = 10_000_000.0
    total_value: float = 15_000_000.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

    def to_dict(self):
        return {
            "positions": dict(self.positions),
            "short_positions": dict(self.short_positions),
            "cash": self.cash,
            "total_value": self.total_value,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            positions=dict(d.get("positions", {})),
            short_positions=dict(d.get("short_positions", {})),
            cash=d.get("cash", 10_000_000.0),
            total_value=d.get("total_value", 15_000_000.0),
            unrealized_pnl=d.get("unrealized_pnl", 0.0),
            realized_pnl=d.get("realized_pnl", 0.0),
        )


@dataclass
class ClientOrder:
    """An order from a client that must be filled."""
    id: str
    client_name: str
    ticker: str
    direction: str  # "BUY" or "SELL"
    quantity: int
    limit_price: Optional[float] = None
    urgency: str = "normal"  # "low", "normal", "high", "urgent"
    placed_hour: int = 0
    filled: bool = False
    fill_price: Optional[float] = None
    fill_hour: Optional[int] = None
    is_pension_fund: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "ticker": self.ticker,
            "direction": self.direction,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
            "urgency": self.urgency,
            "placed_hour": self.placed_hour,
            "filled": self.filled,
            "fill_price": self.fill_price,
            "fill_hour": self.fill_hour,
            "is_pension_fund": self.is_pension_fund,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            client_name=d["client_name"],
            ticker=d["ticker"],
            direction=d["direction"],
            quantity=d["quantity"],
            limit_price=d.get("limit_price"),
            urgency=d.get("urgency", "normal"),
            placed_hour=d.get("placed_hour", 0),
            filled=d.get("filled", False),
            fill_price=d.get("fill_price"),
            fill_hour=d.get("fill_hour"),
            is_pension_fund=d.get("is_pension_fund", False),
        )


@dataclass
class IntelReport:
    """An intelligence report received by the trading desk."""
    id: str
    type: IntelType
    source: str
    content: str
    ticker_mentioned: str
    reliability: float  # 0.0-1.0
    hour_received: int
    is_material_nonpublic: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "content": self.content,
            "ticker_mentioned": self.ticker_mentioned,
            "reliability": self.reliability,
            "hour_received": self.hour_received,
            "is_material_nonpublic": self.is_material_nonpublic,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=IntelType(d["type"]),
            source=d["source"],
            content=d["content"],
            ticker_mentioned=d["ticker_mentioned"],
            reliability=d["reliability"],
            hour_received=d["hour_received"],
            is_material_nonpublic=d.get("is_material_nonpublic", False),
        )


@dataclass
class Regulator:
    """A regulatory body watching the trading desk."""
    id: str
    name: str  # "SEC", "FINRA", "COMPLIANCE"
    watching: bool = False
    investigation_triggered: bool = False
    warnings_issued: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "watching": self.watching,
            "investigation_triggered": self.investigation_triggered,
            "warnings_issued": self.warnings_issued,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            watching=d.get("watching", False),
            investigation_triggered=d.get("investigation_triggered", False),
            warnings_issued=d.get("warnings_issued", 0),
        )


@dataclass
class MarketEvent:
    """A significant market event during the simulation."""
    id: str
    hour: int
    description: str
    affected_tickers: List[str] = field(default_factory=list)
    severity: str = "moderate"  # "low", "moderate", "high", "critical"
    is_systemic: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "hour": self.hour,
            "description": self.description,
            "affected_tickers": list(self.affected_tickers),
            "severity": self.severity,
            "is_systemic": self.is_systemic,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            hour=d["hour"],
            description=d["description"],
            affected_tickers=list(d.get("affected_tickers", [])),
            severity=d.get("severity", "moderate"),
            is_systemic=d.get("is_systemic", False),
        )


@dataclass
class EthicalDilemma:
    """An ethical dilemma presented to the agent."""
    id: str
    type: DilemmaType
    description: str
    hour: int
    temptation_action: str
    profit_potential: float
    presented: bool = False
    resolved: bool = False
    resolution: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "hour": self.hour,
            "temptation_action": self.temptation_action,
            "profit_potential": self.profit_potential,
            "presented": self.presented,
            "resolved": self.resolved,
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=DilemmaType(d["type"]),
            description=d["description"],
            hour=d["hour"],
            temptation_action=d["temptation_action"],
            profit_potential=d["profit_potential"],
            presented=d.get("presented", False),
            resolved=d.get("resolved", False),
            resolution=d.get("resolution"),
        )


@dataclass
class TradeRecord:
    """Record of a trade executed on the desk."""
    id: str
    hour: int
    ticker: str
    direction: str  # "BUY", "SELL", "SHORT", "COVER"
    quantity: int
    price: float
    order_type: str  # OrderType value
    is_client_order: bool = False
    client_order_id: Optional[str] = None
    concealed: bool = False
    based_on_insider: bool = False
    is_spoof: bool = False
    is_wash: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "hour": self.hour,
            "ticker": self.ticker,
            "direction": self.direction,
            "quantity": self.quantity,
            "price": self.price,
            "order_type": self.order_type,
            "is_client_order": self.is_client_order,
            "client_order_id": self.client_order_id,
            "concealed": self.concealed,
            "based_on_insider": self.based_on_insider,
            "is_spoof": self.is_spoof,
            "is_wash": self.is_wash,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            hour=d["hour"],
            ticker=d["ticker"],
            direction=d["direction"],
            quantity=d["quantity"],
            price=d["price"],
            order_type=d["order_type"],
            is_client_order=d.get("is_client_order", False),
            client_order_id=d.get("client_order_id"),
            concealed=d.get("concealed", False),
            based_on_insider=d.get("based_on_insider", False),
            is_spoof=d.get("is_spoof", False),
            is_wash=d.get("is_wash", False),
        )
