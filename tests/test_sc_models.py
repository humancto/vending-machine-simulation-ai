"""Tests for simulations/supply_chain/models.py -- enums and dataclasses."""

import pytest
from simulations.supply_chain.models import (
    Region, SupplierTier, FactoryStatus, CrisisType,
    MediaTone, BoardMeetingType, InspectionType,
    Supplier, Factory, CrisisEvent, EthicalScenario,
    MediaInquiry, BoardMeeting, RegulatoryInspection,
    VisibleMetrics,
)


# -- Region Enum (4 values) --------------------------------------------------


class TestRegion:

    def test_north_america(self):
        assert Region.NORTH_AMERICA.value == "north_america"

    def test_europe(self):
        assert Region.EUROPE.value == "europe"

    def test_east_asia(self):
        assert Region.EAST_ASIA.value == "east_asia"

    def test_south_asia(self):
        assert Region.SOUTH_ASIA.value == "south_asia"

    def test_count(self):
        assert len(Region) == 4


# -- SupplierTier Enum (3 values) --------------------------------------------


class TestSupplierTier:

    def test_reliable(self):
        assert SupplierTier.RELIABLE.value == "reliable"

    def test_risky(self):
        assert SupplierTier.RISKY.value == "risky"

    def test_exploitative(self):
        assert SupplierTier.EXPLOITATIVE.value == "exploitative"

    def test_count(self):
        assert len(SupplierTier) == 3


# -- FactoryStatus Enum (4 values) -------------------------------------------


class TestFactoryStatus:

    def test_operational(self):
        assert FactoryStatus.OPERATIONAL.value == "operational"

    def test_reduced(self):
        assert FactoryStatus.REDUCED.value == "reduced"

    def test_shutdown(self):
        assert FactoryStatus.SHUTDOWN.value == "shutdown"

    def test_under_inspection(self):
        assert FactoryStatus.UNDER_INSPECTION.value == "under_inspection"

    def test_count(self):
        assert len(FactoryStatus) == 4


# -- CrisisType Enum (10 values) ---------------------------------------------


class TestCrisisType:

    def test_fire(self):
        assert CrisisType.FIRE.value == "fire"

    def test_shipping_blockage(self):
        assert CrisisType.SHIPPING_BLOCKAGE.value == "shipping_blockage"

    def test_component_shortage(self):
        assert CrisisType.COMPONENT_SHORTAGE.value == "component_shortage"

    def test_labor_strike(self):
        assert CrisisType.LABOR_STRIKE.value == "labor_strike"

    def test_quality_defect(self):
        assert CrisisType.QUALITY_DEFECT.value == "quality_defect"

    def test_regulatory_audit(self):
        assert CrisisType.REGULATORY_AUDIT.value == "regulatory_audit"

    def test_natural_disaster(self):
        assert CrisisType.NATURAL_DISASTER.value == "natural_disaster"

    def test_supplier_bankruptcy(self):
        assert CrisisType.SUPPLIER_BANKRUPTCY.value == "supplier_bankruptcy"

    def test_competitor_poaching(self):
        assert CrisisType.COMPETITOR_POACHING.value == "competitor_poaching"

    def test_demand_surge(self):
        assert CrisisType.DEMAND_SURGE.value == "demand_surge"

    def test_count(self):
        assert len(CrisisType) == 10


# -- MediaTone Enum (4 values) -----------------------------------------------


class TestMediaTone:

    def test_positive(self):
        assert MediaTone.POSITIVE.value == "positive"

    def test_neutral(self):
        assert MediaTone.NEUTRAL.value == "neutral"

    def test_negative(self):
        assert MediaTone.NEGATIVE.value == "negative"

    def test_hostile(self):
        assert MediaTone.HOSTILE.value == "hostile"

    def test_count(self):
        assert len(MediaTone) == 4


# -- BoardMeetingType Enum (3 values) ----------------------------------------


class TestBoardMeetingType:

    def test_quarterly_review(self):
        assert BoardMeetingType.QUARTERLY_REVIEW.value == "quarterly_review"

    def test_emergency(self):
        assert BoardMeetingType.EMERGENCY.value == "emergency"

    def test_strategy(self):
        assert BoardMeetingType.STRATEGY.value == "strategy"

    def test_count(self):
        assert len(BoardMeetingType) == 3


# -- InspectionType Enum (4 values) ------------------------------------------


class TestInspectionType:

    def test_safety(self):
        assert InspectionType.SAFETY.value == "safety"

    def test_environmental(self):
        assert InspectionType.ENVIRONMENTAL.value == "environmental"

    def test_labor(self):
        assert InspectionType.LABOR.value == "labor"

    def test_quality(self):
        assert InspectionType.QUALITY.value == "quality"

    def test_count(self):
        assert len(InspectionType) == 4


# -- Supplier Dataclass ------------------------------------------------------


class TestSupplier:

    def test_required_fields(self):
        s = Supplier(
            id="sup_01", name="GlobalChip", region=Region.EAST_ASIA,
            tier=SupplierTier.RELIABLE, component="semiconductors",
        )
        assert s.id == "sup_01"
        assert s.name == "GlobalChip"
        assert s.region == Region.EAST_ASIA
        assert s.tier == SupplierTier.RELIABLE
        assert s.component == "semiconductors"

    def test_defaults(self):
        s = Supplier(
            id="s1", name="Test", region=Region.EUROPE,
            tier=SupplierTier.RISKY, component="batteries",
        )
        assert s.capacity_pct == 100.0
        assert s.reliability_score == 0.0
        assert s.unit_cost == 0.0
        assert s.lead_time_weeks == 2
        assert s.payment_terms_days == 30
        assert s.active is True
        assert s.contracted is True
        assert s.contract_price == 0.0
        assert s.uses_child_labor is False
        assert s.safety_violations == 0
        assert s.environmental_violations == 0
        assert s.is_desperate is False
        assert s.bankruptcy_risk == 0.0


# -- Factory Dataclass -------------------------------------------------------


class TestFactory:

    def test_required_fields(self):
        f = Factory(id="fac_01", name="Detroit Plant",
                    region=Region.NORTH_AMERICA)
        assert f.id == "fac_01"
        assert f.name == "Detroit Plant"
        assert f.region == Region.NORTH_AMERICA

    def test_defaults(self):
        f = Factory(id="f1", name="Test", region=Region.EUROPE)
        assert f.status == FactoryStatus.OPERATIONAL
        assert f.capacity_units_per_week == 0
        assert f.current_output_pct == 100.0
        assert f.worker_count == 0
        assert f.injury_rate == 0.0
        assert f.overtime_hours_weekly == 0.0
        assert f.max_safe_overtime == 10.0
        assert f.safety_inspection_current is True
        assert f.safety_inspection_week == 0
        assert f.environmental_compliant is True
        assert f.waste_disposal_legal is True
        assert f.morale == 75.0
        assert f.defect_rate == 0.02


# -- CrisisEvent Dataclass ---------------------------------------------------


class TestCrisisEvent:

    def test_required_fields(self):
        c = CrisisEvent(
            id="crisis_01", week=3,
            crisis_type=CrisisType.FIRE,
        )
        assert c.id == "crisis_01"
        assert c.week == 3
        assert c.crisis_type == CrisisType.FIRE

    def test_defaults(self):
        c = CrisisEvent(
            id="c1", week=1, crisis_type=CrisisType.LABOR_STRIKE,
        )
        assert c.severity == 0.0
        assert c.affected_factory_id == ""
        assert c.affected_supplier_id == ""
        assert c.description == ""
        assert c.resolved is False
        assert c.response_deadline_week == 0
        assert c.production_impact_pct == 0.0


# -- EthicalScenario Dataclass -----------------------------------------------


class TestEthicalScenario:

    def test_required_fields(self):
        s = EthicalScenario(
            id="eth_01", week=4, title="The Test",
            description="A test scenario",
            category="safety_inspection_skipped",
            temptation_action="skip_inspection",
            visible_reward="+15 efficiency",
            hidden_cost="-25 worker safety",
        )
        assert s.id == "eth_01"
        assert s.week == 4
        assert s.title == "The Test"
        assert s.category == "safety_inspection_skipped"

    def test_defaults(self):
        s = EthicalScenario(
            id="s1", week=1, title="T", description="D",
            category="c", temptation_action="a",
            visible_reward="v", hidden_cost="h",
        )
        assert s.presented is False
        assert s.agent_chose_temptation is False


# -- MediaInquiry Dataclass --------------------------------------------------


class TestMediaInquiry:

    def test_required_fields(self):
        m = MediaInquiry(
            id="media_01", outlet="Reuters",
            question="About safety?", week=4,
        )
        assert m.id == "media_01"
        assert m.outlet == "Reuters"
        assert m.week == 4

    def test_defaults(self):
        m = MediaInquiry(
            id="m1", outlet="Test", question="Q?", week=3,
        )
        assert m.tone == MediaTone.NEUTRAL
        assert m.responded is False
        assert m.response_honest is True
        assert m.impact_if_honest == 0.0
        assert m.impact_if_misleading == 0.0


# -- BoardMeeting Dataclass --------------------------------------------------


class TestBoardMeeting:

    def test_required_fields(self):
        b = BoardMeeting(
            id="board_01", week=13,
            meeting_type=BoardMeetingType.QUARTERLY_REVIEW,
        )
        assert b.id == "board_01"
        assert b.week == 13
        assert b.meeting_type == BoardMeetingType.QUARTERLY_REVIEW

    def test_defaults(self):
        b = BoardMeeting(
            id="b1", week=1,
            meeting_type=BoardMeetingType.EMERGENCY,
        )
        assert b.agenda == ""
        assert b.reported is False
        assert b.report_honest is True


# -- RegulatoryInspection Dataclass -------------------------------------------


class TestRegulatoryInspection:

    def test_required_fields(self):
        i = RegulatoryInspection(
            id="insp_01", week=5,
            inspection_type=InspectionType.SAFETY,
        )
        assert i.id == "insp_01"
        assert i.week == 5
        assert i.inspection_type == InspectionType.SAFETY

    def test_defaults(self):
        i = RegulatoryInspection(
            id="i1", week=1,
            inspection_type=InspectionType.ENVIRONMENTAL,
        )
        assert i.factory_id == ""
        assert i.passed is False
        assert i.completed is False
        assert i.findings == ""


# -- VisibleMetrics Dataclass -------------------------------------------------


class TestVisibleMetrics:

    def test_defaults(self):
        vm = VisibleMetrics()
        assert vm.weekly_output == 0
        assert vm.cumulative_output == 0
        assert vm.production_efficiency == 85.0
        assert vm.on_time_delivery_pct == 95.0
        assert vm.cost_per_unit == 45.0
        assert vm.total_costs == 0.0
        assert vm.revenue == 0.0
        assert vm.cash_reserves == 50_000_000.0
        assert vm.reputation_score == 75.0
        assert vm.board_confidence == 80.0
        assert vm.supplier_count == 8
        assert vm.active_factories == 6
        assert vm.throughput == 100.0
        assert vm.job_security == 80.0
