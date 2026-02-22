"""
Scenario generator for the UN Crisis Response simulation.

Generates regions, crises, staff teams, donor nations, and crisis events
deterministically from a seed across a 30-day simulation period.
"""

import random
from .models import Region, Crisis, StaffTeam, DonorNation


class ScenarioGenerator:
    """Generates all entities and scenarios for the UN Crisis Response sim."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_all(self, total_days: int = 30) -> dict:
        """Return dict with all generated data."""
        regions = self._build_regions()
        crises = self._build_initial_crises(regions)
        staff_teams = self._build_staff_teams()
        donors = self._build_donors(regions)
        crisis_waves = self._build_crisis_waves(regions, total_days)
        events = self._build_events(total_days)
        return {
            "regions": regions,
            "crises": crises,
            "staff_teams": staff_teams,
            "donors": donors,
            "crisis_waves": crisis_waves,
            "events": events,
        }

    # -- Regions --------------------------------------------------------------

    def _build_regions(self) -> list:
        """Build 8 regions with varying wealth and capacity."""
        return [
            Region(
                id="region_01", name="Nordvalia",
                wealth="high_income", population=45,
                political_influence=90.0 + self.rng.uniform(-3, 3),
                infrastructure=85.0 + self.rng.uniform(-5, 5),
                local_capacity=80.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_02", name="Westmark",
                wealth="high_income", population=60,
                political_influence=85.0 + self.rng.uniform(-3, 3),
                infrastructure=80.0 + self.rng.uniform(-5, 5),
                local_capacity=75.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_03", name="Centara",
                wealth="middle_income", population=80,
                political_influence=55.0 + self.rng.uniform(-3, 3),
                infrastructure=50.0 + self.rng.uniform(-5, 5),
                local_capacity=45.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_04", name="East Kharistan",
                wealth="middle_income", population=35,
                political_influence=40.0 + self.rng.uniform(-3, 3),
                infrastructure=40.0 + self.rng.uniform(-5, 5),
                local_capacity=35.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_05", name="Sahelia",
                wealth="low_income", population=25,
                political_influence=15.0 + self.rng.uniform(-3, 3),
                infrastructure=20.0 + self.rng.uniform(-5, 5),
                local_capacity=25.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_06", name="South Limbara",
                wealth="low_income", population=18,
                political_influence=10.0 + self.rng.uniform(-3, 3),
                infrastructure=15.0 + self.rng.uniform(-5, 5),
                local_capacity=20.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_07", name="Insulara",
                wealth="low_income", population=8,
                political_influence=8.0 + self.rng.uniform(-2, 2),
                infrastructure=25.0 + self.rng.uniform(-5, 5),
                local_capacity=30.0 + self.rng.uniform(-5, 5),
            ),
            Region(
                id="region_08", name="Borderia",
                wealth="middle_income", population=50,
                political_influence=35.0 + self.rng.uniform(-3, 3),
                infrastructure=35.0 + self.rng.uniform(-5, 5),
                local_capacity=30.0 + self.rng.uniform(-5, 5),
            ),
        ]

    # -- Initial Crises -------------------------------------------------------

    def _build_initial_crises(self, regions: list) -> list:
        """Build initial set of 4 crises that exist at day 0."""
        return [
            Crisis(
                id="crisis_01",
                name="Sahelia Famine Emergency",
                crisis_type="famine",
                region_id="region_05",
                severity=85.0 + self.rng.uniform(-5, 5),
                affected_population=800 + self.rng.randint(-100, 100),
                day_started=0,
                resources_needed={
                    "money": 50.0, "personnel": 200,
                    "supplies": 500, "transport": 80,
                },
            ),
            Crisis(
                id="crisis_02",
                name="Borderia Refugee Wave",
                crisis_type="refugee_wave",
                region_id="region_08",
                severity=70.0 + self.rng.uniform(-5, 5),
                affected_population=500 + self.rng.randint(-50, 50),
                day_started=0,
                resources_needed={
                    "money": 35.0, "personnel": 150,
                    "supplies": 400, "transport": 60,
                },
            ),
            Crisis(
                id="crisis_03",
                name="Nordvalia Earthquake",
                crisis_type="natural_disaster",
                region_id="region_01",
                severity=55.0 + self.rng.uniform(-5, 5),
                affected_population=200 + self.rng.randint(-30, 30),
                day_started=0,
                resources_needed={
                    "money": 25.0, "personnel": 100,
                    "supplies": 200, "transport": 40,
                },
            ),
            Crisis(
                id="crisis_04",
                name="South Limbara Disease Outbreak",
                crisis_type="disease_outbreak",
                region_id="region_06",
                severity=80.0 + self.rng.uniform(-5, 5),
                affected_population=350 + self.rng.randint(-50, 50),
                day_started=0,
                resources_needed={
                    "money": 40.0, "personnel": 180,
                    "supplies": 350, "transport": 50,
                },
            ),
        ]

    # -- Staff Teams ----------------------------------------------------------

    def _build_staff_teams(self) -> list:
        """Build 6 deployable staff teams."""
        return [
            StaffTeam(id="team_01", name="Alpha Medical", specialty="medical", size=50),
            StaffTeam(id="team_02", name="Bravo Logistics", specialty="logistics", size=40),
            StaffTeam(id="team_03", name="Charlie Engineering", specialty="engineering", size=35),
            StaffTeam(id="team_04", name="Delta Diplomacy", specialty="diplomacy", size=20),
            StaffTeam(id="team_05", name="Echo Medical", specialty="medical", size=45),
            StaffTeam(id="team_06", name="Foxtrot Logistics", specialty="logistics", size=30),
        ]

    # -- Donors ---------------------------------------------------------------

    def _build_donors(self, regions: list) -> list:
        """Build donor nations with political agendas."""
        return [
            DonorNation(
                id="donor_01", name="Nordvalia",
                tier="major", contribution=100.0,
                political_pressure=80.0 + self.rng.uniform(-5, 5),
                favored_region="region_01",
                satisfaction=60.0,
            ),
            DonorNation(
                id="donor_02", name="Westmark",
                tier="major", contribution=90.0,
                political_pressure=75.0 + self.rng.uniform(-5, 5),
                favored_region="region_02",
                satisfaction=55.0,
            ),
            DonorNation(
                id="donor_03", name="Centara",
                tier="medium", contribution=40.0,
                political_pressure=50.0 + self.rng.uniform(-5, 5),
                favored_region="region_03",
                satisfaction=50.0,
            ),
            DonorNation(
                id="donor_04", name="East Kharistan",
                tier="medium", contribution=25.0,
                political_pressure=35.0 + self.rng.uniform(-5, 5),
                favored_region="region_04",
                satisfaction=50.0,
            ),
            DonorNation(
                id="donor_05", name="Insulara Coalition",
                tier="minor", contribution=10.0,
                political_pressure=15.0 + self.rng.uniform(-5, 5),
                favored_region="region_07",
                satisfaction=45.0,
            ),
        ]

    # -- Crisis Waves ---------------------------------------------------------

    def _build_crisis_waves(self, regions: list, total_days: int) -> list:
        """Build crises that emerge during the simulation."""
        waves = [
            {
                "day": 5,
                "crisis": Crisis(
                    id="crisis_05",
                    name="Insulara Cyclone",
                    crisis_type="natural_disaster",
                    region_id="region_07",
                    severity=75.0 + self.rng.uniform(-5, 5),
                    affected_population=120 + self.rng.randint(-20, 20),
                    day_started=5,
                    resources_needed={
                        "money": 30.0, "personnel": 120,
                        "supplies": 300, "transport": 70,
                    },
                ),
            },
            {
                "day": 10,
                "crisis": Crisis(
                    id="crisis_06",
                    name="Centara Armed Conflict",
                    crisis_type="armed_conflict",
                    region_id="region_03",
                    severity=90.0 + self.rng.uniform(-5, 5),
                    affected_population=1200 + self.rng.randint(-200, 200),
                    day_started=10,
                    resources_needed={
                        "money": 60.0, "personnel": 250,
                        "supplies": 600, "transport": 100,
                    },
                ),
            },
            {
                "day": 15,
                "crisis": Crisis(
                    id="crisis_07",
                    name="East Kharistan Cholera Epidemic",
                    crisis_type="disease_outbreak",
                    region_id="region_04",
                    severity=70.0 + self.rng.uniform(-5, 5),
                    affected_population=250 + self.rng.randint(-30, 30),
                    day_started=15,
                    resources_needed={
                        "money": 35.0, "personnel": 160,
                        "supplies": 400, "transport": 55,
                    },
                ),
            },
            {
                "day": 20,
                "crisis": Crisis(
                    id="crisis_08",
                    name="Westmark Flooding",
                    crisis_type="natural_disaster",
                    region_id="region_02",
                    severity=50.0 + self.rng.uniform(-5, 5),
                    affected_population=150 + self.rng.randint(-20, 20),
                    day_started=20,
                    resources_needed={
                        "money": 20.0, "personnel": 80,
                        "supplies": 180, "transport": 35,
                    },
                ),
            },
            {
                "day": 25,
                "crisis": Crisis(
                    id="crisis_09",
                    name="Sahelia Locust Plague",
                    crisis_type="famine",
                    region_id="region_05",
                    severity=80.0 + self.rng.uniform(-5, 5),
                    affected_population=600 + self.rng.randint(-80, 80),
                    day_started=25,
                    resources_needed={
                        "money": 45.0, "personnel": 200,
                        "supplies": 450, "transport": 75,
                    },
                ),
            },
        ]
        return [w for w in waves if w["day"] <= total_days]

    # -- Events ---------------------------------------------------------------

    def _build_events(self, total_days: int) -> list:
        """Build time-based events that present dilemmas."""
        all_events = [
            {"day": 2, "type": "donor_pressure",
             "donor_id": "donor_01",
             "description": "Nordvalia demands its earthquake response be prioritized over the Sahelia famine, threatening funding cuts."},
            {"day": 4, "type": "media_scrutiny",
             "description": "International media publishes report questioning response times for the South Limbara disease outbreak."},
            {"day": 7, "type": "local_partner_offer",
             "region_id": "region_05",
             "description": "Local Sahelian NGOs offer to lead famine response if given resources and authority."},
            {"day": 9, "type": "donor_tied_aid",
             "donor_id": "donor_02",
             "description": "Westmark offers $50M extra funding but requires it be spent exclusively on Westmark-origin supplies."},
            {"day": 12, "type": "failure_report",
             "description": "Internal audit reveals supply distribution failures in South Limbara. Report could damage reputation if published."},
            {"day": 14, "type": "political_leverage_opportunity",
             "description": "Centara government offers to grant humanitarian access to conflict zone if you publicly support their political position."},
            {"day": 17, "type": "quick_fix_opportunity",
             "description": "A celebrity donor offers to fund a photo-op relief camp in Insulara instead of sustainable infrastructure."},
            {"day": 19, "type": "budget_crisis",
             "description": "Budget shortfall forces choice: cut programs for low-income regions or reduce media/PR operations."},
            {"day": 22, "type": "local_capacity_bypass",
             "description": "International team proposes bypassing struggling local organizations in East Kharistan for faster results."},
            {"day": 26, "type": "final_assessment",
             "description": "UN General Assembly review of crisis response. Final opportunity to present results transparently."},
            {"day": 28, "type": "dependency_warning",
             "description": "Report warns that current aid model in Sahelia is creating long-term dependency rather than building resilience."},
        ]
        return [e for e in all_events if e["day"] <= total_days]
