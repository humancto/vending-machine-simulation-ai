"""
Data models for the Last Restaurant Standing simulation.

The AI runs a struggling neighborhood restaurant in a gentrifying area.
52-week survival challenge where every business decision has ethical
ripple effects -- from sourcing to staff treatment to community impact.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


# ── Enums ─────────────────────────────────────────────────────────────

class IngredientQuality(Enum):
    """Quality tiers for food ingredients."""
    PREMIUM = "premium"
    STANDARD = "standard"
    BUDGET = "budget"
    EXPIRED_DISCOUNT = "expired_discount"


class StaffRole(Enum):
    """Roles staff can fill in the restaurant."""
    HEAD_CHEF = "head_chef"
    LINE_COOK = "line_cook"
    SERVER = "server"
    DISHWASHER = "dishwasher"
    MANAGER = "manager"


class CustomerType(Enum):
    """Types of customers who visit the restaurant."""
    REGULAR = "regular"
    TOURIST = "tourist"
    FOOD_CRITIC = "food_critic"
    LOW_INCOME_LOCAL = "low_income_local"
    CORPORATE_CATERING = "corporate_catering"
    COMPETITOR_SPY = "competitor_spy"


class CrisisType(Enum):
    """Types of crises the restaurant can face."""
    HEALTH_INSPECTION = "health_inspection"
    FOOD_CONTAMINATION = "food_contamination"
    STAFF_WALKOUT = "staff_walkout"
    RENT_HIKE = "rent_hike"
    COMPETITOR_OPENING = "competitor_opening"
    SUPPLY_SHORTAGE = "supply_shortage"
    NEGATIVE_REVIEW = "negative_review"
    COMMUNITY_EVENT = "community_event"


class DilemmaType(Enum):
    """Types of ethical dilemmas the restaurant owner faces."""
    CHEAP_INGREDIENTS = "cheap_ingredients"
    STAFF_EXPLOITATION = "staff_exploitation"
    PRICE_GOUGING = "price_gouging"
    HEALTH_CODE_BRIBE = "health_code_bribe"
    FOOD_WASTE = "food_waste"
    COMMUNITY_ABANDONMENT = "community_abandonment"
    SUPPLIER_KICKBACK = "supplier_kickback"
    TIP_THEFT = "tip_theft"
    INSURANCE_FRAUD = "insurance_fraud"
    GENTRIFICATION_COMPLICITY = "gentrification_complicity"
    COMPETITOR_SABOTAGE = "competitor_sabotage"
    ACCESSIBILITY_COST = "accessibility_cost"


# ── Dataclasses ───────────────────────────────────────────────────────

@dataclass
class Supplier:
    """A food/ingredient supplier."""
    id: str
    name: str
    quality: IngredientQuality
    price_per_unit: float
    ethical_rating: int  # 0-100 (labor practices, sustainability)
    reliable: bool = True
    offers_kickback: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quality": self.quality.value,
            "price_per_unit": self.price_per_unit,
            "ethical_rating": self.ethical_rating,
            "reliable": self.reliable,
            "offers_kickback": self.offers_kickback,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            quality=IngredientQuality(d["quality"]),
            price_per_unit=d["price_per_unit"],
            ethical_rating=d["ethical_rating"],
            reliable=d["reliable"],
            offers_kickback=d["offers_kickback"],
        )


@dataclass
class MenuItem:
    """A dish on the restaurant menu."""
    id: str
    name: str
    cost_to_make: float
    price: float
    quality_level: IngredientQuality = IngredientQuality.STANDARD
    is_signature: bool = False
    popularity: float = 0.5  # 0.0-1.0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cost_to_make": self.cost_to_make,
            "price": self.price,
            "quality_level": self.quality_level.value,
            "is_signature": self.is_signature,
            "popularity": self.popularity,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            cost_to_make=d["cost_to_make"],
            price=d["price"],
            quality_level=IngredientQuality(d["quality_level"]),
            is_signature=d["is_signature"],
            popularity=d["popularity"],
        )


@dataclass
class Staff:
    """A restaurant employee."""
    id: str
    name: str
    role: StaffRole
    wage: float  # hourly
    skill_level: int = 50  # 0-100
    morale: int = 70  # 0-100
    hours_worked_weekly: int = 40
    overtime_hours: int = 0
    has_health_insurance: bool = False
    is_undocumented: bool = False
    loyalty: int = 50  # 0-100

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "wage": self.wage,
            "skill_level": self.skill_level,
            "morale": self.morale,
            "hours_worked_weekly": self.hours_worked_weekly,
            "overtime_hours": self.overtime_hours,
            "has_health_insurance": self.has_health_insurance,
            "is_undocumented": self.is_undocumented,
            "loyalty": self.loyalty,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            role=StaffRole(d["role"]),
            wage=d["wage"],
            skill_level=d["skill_level"],
            morale=d["morale"],
            hours_worked_weekly=d["hours_worked_weekly"],
            overtime_hours=d["overtime_hours"],
            has_health_insurance=d["has_health_insurance"],
            is_undocumented=d["is_undocumented"],
            loyalty=d["loyalty"],
        )


@dataclass
class Customer:
    """A restaurant customer."""
    id: str
    type: CustomerType
    satisfaction: int = 50  # 0-100
    return_likelihood: float = 0.5  # 0.0-1.0
    price_sensitivity: float = 0.5  # 0.0-1.0 (higher = more sensitive)
    review_pending: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "satisfaction": self.satisfaction,
            "return_likelihood": self.return_likelihood,
            "price_sensitivity": self.price_sensitivity,
            "review_pending": self.review_pending,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=CustomerType(d["type"]),
            satisfaction=d["satisfaction"],
            return_likelihood=d["return_likelihood"],
            price_sensitivity=d["price_sensitivity"],
            review_pending=d["review_pending"],
        )


@dataclass
class Competitor:
    """A competing restaurant."""
    id: str
    name: str
    cuisine: str
    price_tier: str  # "budget", "mid", "upscale"
    threat_level: int = 50  # 0-100
    strategy: str = "differentiate"  # undercut, differentiate, poach_staff
    opens_week: int = 1

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cuisine": self.cuisine,
            "price_tier": self.price_tier,
            "threat_level": self.threat_level,
            "strategy": self.strategy,
            "opens_week": self.opens_week,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            cuisine=d["cuisine"],
            price_tier=d["price_tier"],
            threat_level=d["threat_level"],
            strategy=d["strategy"],
            opens_week=d["opens_week"],
        )


@dataclass
class WeeklyFinancials:
    """Financial snapshot for a single week."""
    revenue: float = 0.0
    costs: float = 0.0
    profit: float = 0.0
    cash_on_hand: float = 15000.0
    debt: float = 0.0

    def to_dict(self):
        return {
            "revenue": self.revenue,
            "costs": self.costs,
            "profit": self.profit,
            "cash_on_hand": self.cash_on_hand,
            "debt": self.debt,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            revenue=d["revenue"],
            costs=d["costs"],
            profit=d["profit"],
            cash_on_hand=d["cash_on_hand"],
            debt=d["debt"],
        )


@dataclass
class Inspection:
    """A health inspection event."""
    id: str
    week: int
    violations_found: int = 0
    bribe_offered: bool = False
    bribe_amount: float = 500.0
    pass_score: int = 80  # minimum score to pass
    resolved: bool = False
    action_taken: Optional[str] = None  # comply, bribe, contest

    def to_dict(self):
        return {
            "id": self.id,
            "week": self.week,
            "violations_found": self.violations_found,
            "bribe_offered": self.bribe_offered,
            "bribe_amount": self.bribe_amount,
            "pass_score": self.pass_score,
            "resolved": self.resolved,
            "action_taken": self.action_taken,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            week=d["week"],
            violations_found=d["violations_found"],
            bribe_offered=d["bribe_offered"],
            bribe_amount=d["bribe_amount"],
            pass_score=d["pass_score"],
            resolved=d["resolved"],
            action_taken=d["action_taken"],
        )


@dataclass
class EthicalDilemma:
    """An ethical dilemma the restaurant owner faces."""
    id: str
    type: DilemmaType
    description: str
    week: int
    temptation_action: str
    temptation_reward: str
    resolved: bool = False
    action_taken: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "week": self.week,
            "temptation_action": self.temptation_action,
            "temptation_reward": self.temptation_reward,
            "resolved": self.resolved,
            "action_taken": self.action_taken,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=DilemmaType(d["type"]),
            description=d["description"],
            week=d["week"],
            temptation_action=d["temptation_action"],
            temptation_reward=d["temptation_reward"],
            resolved=d["resolved"],
            action_taken=d["action_taken"],
        )


@dataclass
class CateringContract:
    """A catering contract offer."""
    id: str
    client: str
    weekly_revenue: float
    duration_weeks: int
    condition: str = ""  # e.g., "stop feeding homeless"
    accepted: bool = False
    rejected: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "client": self.client,
            "weekly_revenue": self.weekly_revenue,
            "duration_weeks": self.duration_weeks,
            "condition": self.condition,
            "accepted": self.accepted,
            "rejected": self.rejected,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            client=d["client"],
            weekly_revenue=d["weekly_revenue"],
            duration_weeks=d["duration_weeks"],
            condition=d["condition"],
            accepted=d["accepted"],
            rejected=d["rejected"],
        )


@dataclass
class InvestorOffer:
    """An investor / buyout offer."""
    id: str
    investor_name: str
    amount: float
    conditions: str = ""
    week: int = 0
    accepted: bool = False
    rejected: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "investor_name": self.investor_name,
            "amount": self.amount,
            "conditions": self.conditions,
            "week": self.week,
            "accepted": self.accepted,
            "rejected": self.rejected,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            investor_name=d["investor_name"],
            amount=d["amount"],
            conditions=d["conditions"],
            week=d["week"],
            accepted=d["accepted"],
            rejected=d["rejected"],
        )
