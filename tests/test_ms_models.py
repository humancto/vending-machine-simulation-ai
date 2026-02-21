"""Tests for simulations/mayor_splitsville/models.py."""

import pytest
from simulations.mayor_splitsville.models import (
    District, ZoningType, StakeholderType, ProjectType,
    BudgetCategory, ProtestAction, EnvironmentalReviewType,
    CityInfo, DistrictInfo, DevelopmentProject, TransitRoute,
    Stakeholder, DeveloperDonation, SpecialScenario, VisibleMetrics,
)


class TestEnums:

    def test_district_values(self):
        assert District.DOWNTOWN.value == "downtown"
        assert District.RIVERSIDE.value == "riverside"
        assert District.TECH_CORRIDOR.value == "tech_corridor"

    def test_zoning_values(self):
        assert ZoningType.RESIDENTIAL.value == "residential"
        assert ZoningType.GREEN_SPACE.value == "green_space"
        assert ZoningType.HIGH_DENSITY.value == "high_density"

    def test_stakeholder_types(self):
        assert StakeholderType.TECH_COMPANY.value == "tech_company"
        assert StakeholderType.COMMUNITY_ORG.value == "community_org"

    def test_project_types(self):
        assert ProjectType.LUXURY_CONDO.value == "luxury_condo"
        assert ProjectType.AFFORDABLE_HOUSING.value == "affordable_housing"

    def test_budget_categories(self):
        assert BudgetCategory.AFFORDABLE_HOUSING.value == "affordable_housing"
        assert BudgetCategory.TRANSIT.value == "transit"

    def test_protest_actions(self):
        assert ProtestAction.LISTEN.value == "listen"
        assert ProtestAction.SUPPRESS.value == "suppress"

    def test_eight_districts(self):
        assert len(District) == 8

    def test_six_zoning_types(self):
        assert len(ZoningType) == 6

    def test_eight_budget_categories(self):
        assert len(BudgetCategory) == 8


class TestDataclasses:

    def test_city_defaults(self):
        city = CityInfo()
        assert city.name == "Splitsville"
        assert city.population == 200_000
        assert city.annual_budget == 500_000_000.0

    def test_district_info(self):
        d = DistrictInfo(
            district=District.DOWNTOWN,
            name="Downtown",
            population=35_000,
            median_income=68_000,
            poverty_rate=0.10,
            zoning=ZoningType.MIXED_USE,
        )
        assert d.district == District.DOWNTOWN
        assert d.population == 35_000
        assert d.displacement_risk == 0.0

    def test_development_project(self):
        p = DevelopmentProject(
            id="proj_test",
            name="Test Project",
            project_type=ProjectType.TECH_CAMPUS,
            district=District.TECH_CORRIDOR,
            developer_name="Test Dev",
            jobs_created=100,
        )
        assert p.id == "proj_test"
        assert p.approved is False
        assert p.fast_tracked is False

    def test_transit_route(self):
        r = TransitRoute(
            id="route_test",
            name="Test Route",
            serves_district=District.RIVERSIDE,
            cost=10_000_000,
        )
        assert r.funded is False
        assert r.serves_underserved is False

    def test_stakeholder(self):
        s = Stakeholder(
            id="stake_test",
            name="Test Group",
            stakeholder_type=StakeholderType.EXISTING_RESIDENTS,
        )
        assert s.influence == 50.0
        assert s.satisfaction == 50.0

    def test_developer_donation(self):
        d = DeveloperDonation(
            id="don_test",
            donor_name="Test Donor",
            amount=100_000,
        )
        assert d.accepted is False
        assert d.rejected is False
        assert d.is_ethical is False

    def test_special_scenario(self):
        s = SpecialScenario(
            id="sc_test",
            month=1,
            title="Test Scenario",
            description="Test description",
            category="profit_over_people",
            temptation_action="test_action",
            visible_reward="+10 revenue",
            hidden_cost="-10 justice",
        )
        assert s.presented is False
        assert s.agent_chose_temptation is False

    def test_visible_metrics_defaults(self):
        m = VisibleMetrics()
        assert m.tax_revenue == 50_000_000.0
        assert m.job_growth == 0
        assert m.city_approval_rating == 55.0
        assert m.total_months == 24
