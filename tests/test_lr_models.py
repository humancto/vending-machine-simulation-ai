"""Tests for simulations/last_restaurant/models.py."""

import pytest
from simulations.last_restaurant.models import (
    CateringContract,
    Competitor,
    Customer,
    CustomerType,
    DilemmaType,
    EthicalDilemma,
    IngredientQuality,
    Inspection,
    InvestorOffer,
    MenuItem,
    Staff,
    StaffRole,
    Supplier,
    WeeklyFinancials,
    CrisisType,
)


# ── Enum Tests ────────────────────────────────────────────────────────

class TestIngredientQuality:

    def test_premium(self):
        assert IngredientQuality.PREMIUM.value == "premium"

    def test_standard(self):
        assert IngredientQuality.STANDARD.value == "standard"

    def test_budget(self):
        assert IngredientQuality.BUDGET.value == "budget"

    def test_expired_discount(self):
        assert IngredientQuality.EXPIRED_DISCOUNT.value == "expired_discount"

    def test_all_values(self):
        assert len(IngredientQuality) == 4


class TestStaffRole:

    def test_head_chef(self):
        assert StaffRole.HEAD_CHEF.value == "head_chef"

    def test_line_cook(self):
        assert StaffRole.LINE_COOK.value == "line_cook"

    def test_server(self):
        assert StaffRole.SERVER.value == "server"

    def test_dishwasher(self):
        assert StaffRole.DISHWASHER.value == "dishwasher"

    def test_manager(self):
        assert StaffRole.MANAGER.value == "manager"

    def test_all_values(self):
        assert len(StaffRole) == 5


class TestCustomerType:

    def test_regular(self):
        assert CustomerType.REGULAR.value == "regular"

    def test_tourist(self):
        assert CustomerType.TOURIST.value == "tourist"

    def test_food_critic(self):
        assert CustomerType.FOOD_CRITIC.value == "food_critic"

    def test_low_income_local(self):
        assert CustomerType.LOW_INCOME_LOCAL.value == "low_income_local"

    def test_corporate_catering(self):
        assert CustomerType.CORPORATE_CATERING.value == "corporate_catering"

    def test_competitor_spy(self):
        assert CustomerType.COMPETITOR_SPY.value == "competitor_spy"

    def test_all_values(self):
        assert len(CustomerType) == 6


class TestCrisisType:

    def test_health_inspection(self):
        assert CrisisType.HEALTH_INSPECTION.value == "health_inspection"

    def test_all_values(self):
        assert len(CrisisType) == 8


class TestDilemmaType:

    def test_cheap_ingredients(self):
        assert DilemmaType.CHEAP_INGREDIENTS.value == "cheap_ingredients"

    def test_tip_theft(self):
        assert DilemmaType.TIP_THEFT.value == "tip_theft"

    def test_insurance_fraud(self):
        assert DilemmaType.INSURANCE_FRAUD.value == "insurance_fraud"

    def test_all_values(self):
        assert len(DilemmaType) == 12


# ── Supplier Tests ────────────────────────────────────────────────────

class TestSupplier:

    def test_create_supplier(self):
        s = Supplier(id="s1", name="Test", quality=IngredientQuality.STANDARD,
                     price_per_unit=5.0, ethical_rating=70)
        assert s.id == "s1"
        assert s.name == "Test"
        assert s.quality == IngredientQuality.STANDARD
        assert s.price_per_unit == 5.0
        assert s.ethical_rating == 70
        assert s.reliable is True
        assert s.offers_kickback is False

    def test_supplier_to_dict(self):
        s = Supplier(id="s1", name="Test", quality=IngredientQuality.PREMIUM,
                     price_per_unit=10.0, ethical_rating=90)
        d = s.to_dict()
        assert d["id"] == "s1"
        assert d["quality"] == "premium"
        assert d["price_per_unit"] == 10.0

    def test_supplier_from_dict(self):
        d = {"id": "s1", "name": "Test", "quality": "budget",
             "price_per_unit": 3.0, "ethical_rating": 20,
             "reliable": False, "offers_kickback": True}
        s = Supplier.from_dict(d)
        assert s.quality == IngredientQuality.BUDGET
        assert s.reliable is False
        assert s.offers_kickback is True

    def test_supplier_roundtrip(self):
        s = Supplier(id="s1", name="X", quality=IngredientQuality.EXPIRED_DISCOUNT,
                     price_per_unit=1.0, ethical_rating=5,
                     reliable=False, offers_kickback=True)
        restored = Supplier.from_dict(s.to_dict())
        assert restored.id == s.id
        assert restored.quality == s.quality
        assert restored.offers_kickback == s.offers_kickback


# ── MenuItem Tests ────────────────────────────────────────────────────

class TestMenuItem:

    def test_create_menu_item(self):
        m = MenuItem(id="m1", name="Burger", cost_to_make=5.0, price=12.0)
        assert m.id == "m1"
        assert m.cost_to_make == 5.0
        assert m.price == 12.0
        assert m.quality_level == IngredientQuality.STANDARD
        assert m.is_signature is False
        assert m.popularity == 0.5

    def test_menu_item_to_dict(self):
        m = MenuItem(id="m1", name="Soup", cost_to_make=2.0, price=6.0,
                     is_signature=True, popularity=0.9)
        d = m.to_dict()
        assert d["name"] == "Soup"
        assert d["is_signature"] is True
        assert d["popularity"] == 0.9

    def test_menu_item_from_dict(self):
        d = {"id": "m1", "name": "Steak", "cost_to_make": 10.0,
             "price": 22.0, "quality_level": "premium",
             "is_signature": False, "popularity": 0.4}
        m = MenuItem.from_dict(d)
        assert m.quality_level == IngredientQuality.PREMIUM
        assert m.price == 22.0

    def test_menu_item_roundtrip(self):
        m = MenuItem(id="m1", name="X", cost_to_make=3.0, price=8.0,
                     quality_level=IngredientQuality.BUDGET, popularity=0.7)
        restored = MenuItem.from_dict(m.to_dict())
        assert restored.id == m.id
        assert restored.price == m.price


# ── Staff Tests ───────────────────────────────────────────────────────

class TestStaff:

    def test_create_staff(self):
        s = Staff(id="s1", name="Maria", role=StaffRole.HEAD_CHEF, wage=22.0)
        assert s.name == "Maria"
        assert s.role == StaffRole.HEAD_CHEF
        assert s.wage == 22.0
        assert s.skill_level == 50
        assert s.morale == 70
        assert s.hours_worked_weekly == 40
        assert s.overtime_hours == 0
        assert s.has_health_insurance is False
        assert s.is_undocumented is False
        assert s.loyalty == 50

    def test_staff_to_dict(self):
        s = Staff(id="s1", name="Carlos", role=StaffRole.DISHWASHER,
                  wage=10.0, is_undocumented=True, loyalty=80)
        d = s.to_dict()
        assert d["role"] == "dishwasher"
        assert d["is_undocumented"] is True
        assert d["loyalty"] == 80

    def test_staff_from_dict(self):
        d = {"id": "s1", "name": "Tom", "role": "server", "wage": 8.0,
             "skill_level": 70, "morale": 65, "hours_worked_weekly": 40,
             "overtime_hours": 5, "has_health_insurance": True,
             "is_undocumented": False, "loyalty": 60}
        s = Staff.from_dict(d)
        assert s.role == StaffRole.SERVER
        assert s.has_health_insurance is True
        assert s.overtime_hours == 5

    def test_staff_roundtrip(self):
        s = Staff(id="s1", name="X", role=StaffRole.MANAGER, wage=18.0,
                  skill_level=80, morale=90, has_health_insurance=True)
        restored = Staff.from_dict(s.to_dict())
        assert restored.wage == s.wage
        assert restored.skill_level == s.skill_level


# ── Customer Tests ────────────────────────────────────────────────────

class TestCustomer:

    def test_create_customer(self):
        c = Customer(id="c1", type=CustomerType.LOW_INCOME_LOCAL)
        assert c.type == CustomerType.LOW_INCOME_LOCAL
        assert c.satisfaction == 50
        assert c.price_sensitivity == 0.5

    def test_customer_to_dict(self):
        c = Customer(id="c1", type=CustomerType.FOOD_CRITIC,
                     review_pending=True)
        d = c.to_dict()
        assert d["type"] == "food_critic"
        assert d["review_pending"] is True

    def test_customer_from_dict(self):
        d = {"id": "c1", "type": "tourist", "satisfaction": 80,
             "return_likelihood": 0.3, "price_sensitivity": 0.2,
             "review_pending": False}
        c = Customer.from_dict(d)
        assert c.type == CustomerType.TOURIST
        assert c.satisfaction == 80

    def test_customer_roundtrip(self):
        c = Customer(id="c1", type=CustomerType.REGULAR,
                     satisfaction=75, return_likelihood=0.8)
        restored = Customer.from_dict(c.to_dict())
        assert restored.satisfaction == c.satisfaction


# ── Competitor Tests ──────────────────────────────────────────────────

class TestCompetitor:

    def test_create_competitor(self):
        c = Competitor(id="c1", name="Rival", cuisine="Italian",
                       price_tier="mid", threat_level=60)
        assert c.name == "Rival"
        assert c.strategy == "differentiate"

    def test_competitor_to_dict(self):
        c = Competitor(id="c1", name="Rival", cuisine="Burgers",
                       price_tier="budget", opens_week=10)
        d = c.to_dict()
        assert d["opens_week"] == 10

    def test_competitor_roundtrip(self):
        c = Competitor(id="c1", name="X", cuisine="Y", price_tier="upscale",
                       threat_level=80, strategy="poach_staff", opens_week=20)
        restored = Competitor.from_dict(c.to_dict())
        assert restored.threat_level == 80
        assert restored.strategy == "poach_staff"


# ── WeeklyFinancials Tests ────────────────────────────────────────────

class TestWeeklyFinancials:

    def test_defaults(self):
        f = WeeklyFinancials()
        assert f.cash_on_hand == 15000.0
        assert f.revenue == 0.0
        assert f.debt == 0.0

    def test_to_dict(self):
        f = WeeklyFinancials(revenue=5000, costs=4000, profit=1000,
                             cash_on_hand=16000, debt=500)
        d = f.to_dict()
        assert d["revenue"] == 5000
        assert d["profit"] == 1000

    def test_from_dict(self):
        d = {"revenue": 3000, "costs": 3500, "profit": -500,
             "cash_on_hand": 14500, "debt": 0}
        f = WeeklyFinancials.from_dict(d)
        assert f.profit == -500

    def test_roundtrip(self):
        f = WeeklyFinancials(revenue=6000, costs=5000, profit=1000,
                             cash_on_hand=20000, debt=1000)
        restored = WeeklyFinancials.from_dict(f.to_dict())
        assert restored.cash_on_hand == f.cash_on_hand


# ── Inspection Tests ──────────────────────────────────────────────────

class TestInspection:

    def test_create_inspection(self):
        i = Inspection(id="i1", week=8, violations_found=2, bribe_offered=True)
        assert i.violations_found == 2
        assert i.bribe_offered is True
        assert i.resolved is False

    def test_inspection_to_dict(self):
        i = Inspection(id="i1", week=8, violations_found=3,
                       bribe_amount=750, action_taken="comply")
        d = i.to_dict()
        assert d["bribe_amount"] == 750

    def test_inspection_roundtrip(self):
        i = Inspection(id="i1", week=26, violations_found=1,
                       resolved=True, action_taken="bribe")
        restored = Inspection.from_dict(i.to_dict())
        assert restored.action_taken == "bribe"
        assert restored.resolved is True


# ── EthicalDilemma Tests ──────────────────────────────────────────────

class TestEthicalDilemma:

    def test_create_dilemma(self):
        d = EthicalDilemma(id="d1", type=DilemmaType.TIP_THEFT,
                           description="Steal tips", week=10,
                           temptation_action="steal",
                           temptation_reward="+$200/week")
        assert d.type == DilemmaType.TIP_THEFT
        assert d.resolved is False

    def test_dilemma_to_dict(self):
        d = EthicalDilemma(id="d1", type=DilemmaType.HEALTH_CODE_BRIBE,
                           description="Bribe", week=8,
                           temptation_action="bribe",
                           temptation_reward="Pass inspection")
        dd = d.to_dict()
        assert dd["type"] == "health_code_bribe"

    def test_dilemma_roundtrip(self):
        d = EthicalDilemma(id="d1", type=DilemmaType.INSURANCE_FRAUD,
                           description="Fraud", week=35,
                           temptation_action="inflate",
                           temptation_reward="+$5000",
                           resolved=True, action_taken="resist")
        restored = EthicalDilemma.from_dict(d.to_dict())
        assert restored.action_taken == "resist"
        assert restored.type == DilemmaType.INSURANCE_FRAUD


# ── CateringContract Tests ────────────────────────────────────────────

class TestCateringContract:

    def test_create_contract(self):
        c = CateringContract(id="c1", client="City", weekly_revenue=800,
                             duration_weeks=20,
                             condition="Stop community meals")
        assert c.weekly_revenue == 800
        assert c.accepted is False

    def test_contract_roundtrip(self):
        c = CateringContract(id="c1", client="Corp", weekly_revenue=500,
                             duration_weeks=10, condition="",
                             accepted=True, rejected=False)
        restored = CateringContract.from_dict(c.to_dict())
        assert restored.accepted is True
        assert restored.weekly_revenue == 500


# ── InvestorOffer Tests ───────────────────────────────────────────────

class TestInvestorOffer:

    def test_create_investor(self):
        i = InvestorOffer(id="i1", investor_name="Dev", amount=100000,
                          conditions="Close restaurant", week=40)
        assert i.amount == 100000
        assert i.accepted is False

    def test_investor_roundtrip(self):
        i = InvestorOffer(id="i1", investor_name="Angel", amount=50000,
                          conditions="Fire Carlos", week=50,
                          accepted=False, rejected=True)
        restored = InvestorOffer.from_dict(i.to_dict())
        assert restored.rejected is True
        assert restored.conditions == "Fire Carlos"
