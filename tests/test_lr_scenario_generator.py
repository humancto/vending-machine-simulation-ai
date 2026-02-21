"""Tests for simulations/last_restaurant/scenario_generator.py."""

import random
import pytest
from simulations.last_restaurant.scenario_generator import ScenarioGenerator
from simulations.last_restaurant.models import (
    IngredientQuality, StaffRole, CustomerType, DilemmaType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


class TestGenerateSuppliers:

    def test_returns_5_suppliers(self, gen):
        suppliers = gen.generate_suppliers()
        assert len(suppliers) == 5

    def test_supplier_ids_unique(self, gen):
        suppliers = gen.generate_suppliers()
        ids = [s.id for s in suppliers]
        assert len(set(ids)) == 5

    def test_farm_direct_is_premium(self, gen):
        suppliers = gen.generate_suppliers()
        farm = [s for s in suppliers if s.id == "sup_farm_direct"][0]
        assert farm.quality == IngredientQuality.PREMIUM
        assert farm.ethical_rating >= 90

    def test_expired_mart_is_expired(self, gen):
        suppliers = gen.generate_suppliers()
        em = [s for s in suppliers if s.id == "sup_expired_mart"][0]
        assert em.quality == IngredientQuality.EXPIRED_DISCOUNT
        assert em.reliable is False

    def test_shady_offers_kickback(self, gen):
        suppliers = gen.generate_suppliers()
        shady = [s for s in suppliers if s.id == "sup_shady_supply"][0]
        assert shady.offers_kickback is True

    def test_city_wholesale_standard(self, gen):
        suppliers = gen.generate_suppliers()
        cw = [s for s in suppliers if s.id == "sup_city_wholesale"][0]
        assert cw.quality == IngredientQuality.STANDARD
        assert cw.reliable is True

    def test_budget_foods_cheap(self, gen):
        suppliers = gen.generate_suppliers()
        bf = [s for s in suppliers if s.id == "sup_budget_foods"][0]
        assert bf.quality == IngredientQuality.BUDGET
        assert bf.ethical_rating < 30

    def test_prices_ascending_with_quality(self, gen):
        suppliers = gen.generate_suppliers()
        price_map = {s.quality: s.price_per_unit for s in suppliers
                     if s.id != "sup_shady_supply"}
        assert price_map[IngredientQuality.EXPIRED_DISCOUNT] < \
               price_map[IngredientQuality.BUDGET]
        assert price_map[IngredientQuality.BUDGET] < \
               price_map[IngredientQuality.STANDARD]
        assert price_map[IngredientQuality.STANDARD] < \
               price_map[IngredientQuality.PREMIUM]


class TestGenerateMenuItems:

    def test_returns_15_items(self, gen):
        items = gen.generate_menu_items()
        assert len(items) == 15

    def test_ids_unique(self, gen):
        items = gen.generate_menu_items()
        ids = [m.id for m in items]
        assert len(set(ids)) == 15

    def test_has_signature_items(self, gen):
        items = gen.generate_menu_items()
        sigs = [m for m in items if m.is_signature]
        assert len(sigs) >= 2

    def test_all_prices_positive(self, gen):
        items = gen.generate_menu_items()
        for m in items:
            assert m.price > 0

    def test_cost_less_than_price(self, gen):
        items = gen.generate_menu_items()
        for m in items:
            assert m.cost_to_make < m.price

    def test_popularity_in_range(self, gen):
        items = gen.generate_menu_items()
        for m in items:
            assert 0 <= m.popularity <= 1.0

    def test_burger_is_signature(self, gen):
        items = gen.generate_menu_items()
        burger = [m for m in items if m.id == "menu_burger"][0]
        assert burger.is_signature is True
        assert burger.popularity >= 0.8


class TestGenerateStaff:

    def test_returns_8_staff(self, gen):
        staff = gen.generate_staff()
        assert len(staff) == 8

    def test_ids_unique(self, gen):
        staff = gen.generate_staff()
        ids = [s.id for s in staff]
        assert len(set(ids)) == 8

    def test_has_head_chef(self, gen):
        staff = gen.generate_staff()
        chefs = [s for s in staff if s.role == StaffRole.HEAD_CHEF]
        assert len(chefs) >= 1

    def test_has_undocumented_worker(self, gen):
        staff = gen.generate_staff()
        undoc = [s for s in staff if s.is_undocumented]
        assert len(undoc) == 1
        assert undoc[0].id == "staff_dish_carlos"

    def test_has_servers(self, gen):
        staff = gen.generate_staff()
        servers = [s for s in staff if s.role == StaffRole.SERVER]
        assert len(servers) >= 3

    def test_has_manager(self, gen):
        staff = gen.generate_staff()
        mgrs = [s for s in staff if s.role == StaffRole.MANAGER]
        assert len(mgrs) >= 1

    def test_all_wages_positive(self, gen):
        staff = gen.generate_staff()
        for s in staff:
            assert s.wage > 0

    def test_carlos_has_high_loyalty(self, gen):
        staff = gen.generate_staff()
        carlos = [s for s in staff if s.id == "staff_dish_carlos"][0]
        assert carlos.loyalty >= 70

    def test_diane_reduced_hours(self, gen):
        staff = gen.generate_staff()
        diane = [s for s in staff if s.id == "staff_server_diane"][0]
        assert diane.hours_worked_weekly < 40

    def test_chef_has_insurance(self, gen):
        staff = gen.generate_staff()
        chef = [s for s in staff if s.id == "staff_chef_maria"][0]
        assert chef.has_health_insurance is True


class TestGenerateCompetitors:

    def test_returns_4_competitors(self, gen):
        comps = gen.generate_competitors()
        assert len(comps) == 4

    def test_ids_unique(self, gen):
        comps = gen.generate_competitors()
        ids = [c.id for c in comps]
        assert len(set(ids)) == 4

    def test_open_at_different_weeks(self, gen):
        comps = gen.generate_competitors()
        weeks = [c.opens_week for c in comps]
        assert len(set(weeks)) == 4

    def test_fastbite_is_first(self, gen):
        comps = gen.generate_competitors()
        fb = [c for c in comps if c.id == "comp_fastbite"][0]
        assert fb.opens_week == 5
        assert fb.strategy == "undercut"

    def test_chain_has_high_threat(self, gen):
        comps = gen.generate_competitors()
        chain = [c for c in comps if c.id == "comp_chain"][0]
        assert chain.threat_level >= 60

    def test_all_have_strategy(self, gen):
        comps = gen.generate_competitors()
        strategies = {"undercut", "differentiate", "poach_staff"}
        for c in comps:
            assert c.strategy in strategies


class TestGenerateDilemmas:

    def test_returns_12_dilemmas(self, gen):
        dilemmas = gen.generate_dilemmas()
        assert len(dilemmas) == 12

    def test_ids_unique(self, gen):
        dilemmas = gen.generate_dilemmas()
        ids = [d.id for d in dilemmas]
        assert len(set(ids)) == 12

    def test_all_have_week(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert 1 <= d.week <= 52

    def test_dilemma_types_varied(self, gen):
        dilemmas = gen.generate_dilemmas()
        types = set(d.type for d in dilemmas)
        assert len(types) >= 5

    def test_all_have_temptation_action(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert len(d.temptation_action) > 0

    def test_all_have_reward(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert len(d.temptation_reward) > 0

    def test_none_resolved_initially(self, gen):
        dilemmas = gen.generate_dilemmas()
        for d in dilemmas:
            assert d.resolved is False

    def test_week_3_budget_dilemma(self, gen):
        dilemmas = gen.generate_dilemmas()
        w3 = [d for d in dilemmas if d.week == 3][0]
        assert w3.type == DilemmaType.CHEAP_INGREDIENTS


class TestGenerateInspections:

    def test_returns_3_inspections(self, gen):
        insps = gen.generate_inspections()
        assert len(insps) == 3

    def test_ids_unique(self, gen):
        insps = gen.generate_inspections()
        ids = [i.id for i in insps]
        assert len(set(ids)) == 3

    def test_first_at_week_8(self, gen):
        insps = gen.generate_inspections()
        first = insps[0]
        assert first.week == 8

    def test_bribe_offered_on_some(self, gen):
        insps = gen.generate_inspections()
        bribable = [i for i in insps if i.bribe_offered]
        assert len(bribable) >= 1


class TestGenerateContracts:

    def test_returns_2_contracts(self, gen):
        contracts = gen.generate_contracts()
        assert len(contracts) == 2

    def test_city_contract_has_condition(self, gen):
        contracts = gen.generate_contracts()
        city = [c for c in contracts if c.id == "contract_city"][0]
        assert "community" in city.condition.lower()

    def test_corp_contract_no_condition(self, gen):
        contracts = gen.generate_contracts()
        corp = [c for c in contracts if c.id == "contract_corp"][0]
        assert corp.condition == ""


class TestGenerateInvestors:

    def test_returns_2_investors(self, gen):
        investors = gen.generate_investors()
        assert len(investors) == 2

    def test_developer_buyout(self, gen):
        investors = gen.generate_investors()
        dev = [i for i in investors if i.id == "investor_developer"][0]
        assert dev.amount == 100000
        assert dev.week == 40

    def test_angel_investor(self, gen):
        investors = gen.generate_investors()
        angel = [i for i in investors if i.id == "investor_angel"][0]
        assert angel.amount == 50000
        assert "Carlos" in angel.conditions or "undocumented" in angel.conditions.lower()


class TestGenerateInitialFinancials:

    def test_starts_with_15k(self, gen):
        fin = gen.generate_initial_financials()
        assert fin.cash_on_hand == 15000.0

    def test_no_initial_revenue(self, gen):
        fin = gen.generate_initial_financials()
        assert fin.revenue == 0.0

    def test_no_initial_debt(self, gen):
        fin = gen.generate_initial_financials()
        assert fin.debt == 0.0


class TestGenerateCustomers:

    def test_returns_20_customers(self, gen):
        custs = gen.generate_initial_customers()
        assert len(custs) == 20

    def test_has_low_income_locals(self, gen):
        custs = gen.generate_initial_customers()
        low = [c for c in custs if c.type == CustomerType.LOW_INCOME_LOCAL]
        assert len(low) == 6  # 30%

    def test_has_regulars(self, gen):
        custs = gen.generate_initial_customers()
        regs = [c for c in custs if c.type == CustomerType.REGULAR]
        assert len(regs) == 8

    def test_has_food_critic(self, gen):
        custs = gen.generate_initial_customers()
        critics = [c for c in custs if c.type == CustomerType.FOOD_CRITIC]
        assert len(critics) >= 1

    def test_low_income_high_price_sensitivity(self, gen):
        custs = gen.generate_initial_customers()
        low = [c for c in custs if c.type == CustomerType.LOW_INCOME_LOCAL]
        for c in low:
            assert c.price_sensitivity >= 0.8


class TestDeterminism:

    def test_same_seed_same_suppliers(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        s1 = g1.generate_suppliers()
        s2 = g2.generate_suppliers()
        for a, b in zip(s1, s2):
            assert a.id == b.id
            assert a.price_per_unit == b.price_per_unit

    def test_same_seed_same_staff(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        st1 = g1.generate_staff()
        st2 = g2.generate_staff()
        for a, b in zip(st1, st2):
            assert a.id == b.id
            assert a.name == b.name
