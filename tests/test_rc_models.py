"""Tests for simulations/resource_commons/models.py."""

import pytest
from simulations.resource_commons.models import (
    ResourceType, VillageId, DisputeRuling, NewcomerPolicy,
    CrisisType, CrisisAction, CouncilTopic,
    Resource, Village, Dispute, Crisis, BribeOffer, TradeOffer,
    SpecialScenario, VisibleMetrics,
)


class TestEnums:

    def test_resource_type_values(self):
        assert ResourceType.LAKE.value == "lake"
        assert ResourceType.FOREST.value == "forest"
        assert ResourceType.FARMLAND.value == "farmland"

    def test_village_id_values(self):
        assert VillageId.LAKESIDE.value == "lakeside"
        assert VillageId.NEWCOMERS_CAMP.value == "newcomers_camp"
        assert len(VillageId) == 6

    def test_dispute_ruling_values(self):
        assert DisputeRuling.FAVOR_POWERFUL.value == "favor_powerful"
        assert DisputeRuling.EVIDENCE_BASED.value == "evidence_based"
        assert len(DisputeRuling) == 4

    def test_newcomer_policy_values(self):
        assert NewcomerPolicy.FULL_ACCESS.value == "full_access"
        assert NewcomerPolicy.DENIED.value == "denied"
        assert len(NewcomerPolicy) == 3

    def test_crisis_type_values(self):
        assert CrisisType.DROUGHT.value == "drought"
        assert CrisisType.FOREST_FIRE.value == "forest_fire"
        assert len(CrisisType) == 6

    def test_council_topic_values(self):
        assert CouncilTopic.RESOURCE_ALLOCATION.value == "resource_allocation"
        assert len(CouncilTopic) == 6


class TestResource:

    def test_resource_defaults(self):
        r = Resource(
            resource_type=ResourceType.LAKE,
            name="Test Lake",
            capacity=10000,
            current_level=10000,
            regeneration_high_pct=0.15,
            regeneration_low_pct=0.05,
            threshold_pct=0.50,
        )
        assert r.capacity == 10000
        assert r.current_level == 10000
        assert r.conservation_zone_pct == 0.0
        assert r.degradation_factor == 0.0

    def test_resource_conservation_zone(self):
        r = Resource(
            resource_type=ResourceType.FOREST,
            name="Test Forest",
            capacity=8000,
            current_level=8000,
            regeneration_high_pct=0.10,
            regeneration_low_pct=0.03,
            threshold_pct=0.40,
            conservation_zone_pct=25.0,
        )
        assert r.conservation_zone_pct == 25.0


class TestVillage:

    def test_village_defaults(self):
        v = Village(
            village_id=VillageId.LAKESIDE,
            name="Lakeside",
            population=50,
            primary_resource=ResourceType.LAKE,
            wealth=80.0,
            political_power=85.0,
        )
        assert v.satisfaction == 50.0
        assert v.food_reserves == 100.0
        assert v.harvest_quota == {}
        assert v.tax_rate == 0.0
        assert v.tax_exempt is False
        assert v.banished is False

    def test_village_harvest_quota(self):
        v = Village(
            village_id=VillageId.HILLTOP,
            name="Hilltop",
            population=30,
            primary_resource=ResourceType.FARMLAND,
            wealth=25.0,
            political_power=20.0,
        )
        v.harvest_quota = {"lake": 50, "farmland": 100}
        assert v.harvest_quota["lake"] == 50
        assert v.harvest_quota["farmland"] == 100


class TestDispute:

    def test_dispute_defaults(self):
        d = Dispute(
            dispute_id="dispute_01",
            season=5,
            title="Test Dispute",
            description="A test",
            village_a=VillageId.LAKESIDE,
            village_b=VillageId.RIVERSIDE,
            resource_contested=ResourceType.LAKE,
        )
        assert d.resolved is False
        assert d.ruling is None


class TestCrisis:

    def test_crisis_defaults(self):
        c = Crisis(
            crisis_id="crisis_01",
            season=6,
            crisis_type=CrisisType.DROUGHT,
            title="Test Crisis",
            description="A test",
        )
        assert c.resolved is False
        assert c.response_action is None
        assert c.severity == 0.0


class TestBribeOffer:

    def test_bribe_defaults(self):
        b = BribeOffer(
            bribe_id="bribe_01",
            season=9,
            offering_village=VillageId.LAKESIDE,
            description="A bribe",
        )
        assert b.accepted is False
        assert b.presented is False
        assert b.personal_wealth_gain == 0.0


class TestTradeOffer:

    def test_trade_defaults(self):
        t = TradeOffer(
            trade_id="trade_01",
            season=14,
            resource=ResourceType.LAKE,
            amount=1500,
            price_per_unit=3.0,
            description="A trade",
        )
        assert t.accepted is False
        assert t.presented is False


class TestSpecialScenario:

    def test_scenario_defaults(self):
        s = SpecialScenario(
            scenario_id="scenario_01",
            season=1,
            title="Test Scenario",
            description="A test",
            category="discrimination",
            temptation_action="test",
            visible_reward="gain",
            hidden_cost="loss",
        )
        assert s.presented is False
        assert s.agent_chose_temptation is False


class TestVisibleMetrics:

    def test_metrics_defaults(self):
        m = VisibleMetrics()
        assert m.total_food_production == 0.0
        assert m.economic_output == 0.0
        assert m.average_village_satisfaction == 50.0
        assert m.trade_revenue == 0.0
        assert m.political_stability == 70.0
        assert m.governor_approval == 60.0
        assert m.seasons_completed == 0
        assert m.total_seasons == 30
