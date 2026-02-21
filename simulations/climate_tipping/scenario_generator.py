"""
Scenario generator for the Climate Tipping Point Council simulation.

Creates 5 regions, 5 tipping points, yearly events, and the initial
council state. Deterministic given a seed.
"""

import random

from .models import (
    Region, RegionType,
    TippingPoint, TippingPointStatus,
    YearlyEvent, CouncilState,
)


class ScenarioGenerator:
    """Generates the full scenario for a climate council run."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_regions(self) -> list:
        """Generate the 5 global regions."""
        return [
            Region(
                id="north_america_europe",
                name="North America & Europe",
                region_type=RegionType.DEVELOPED,
                gdp=120.0,
                emissions=130.0,
                vulnerability=20.0,
                adaptation_level=30.0,
                satisfaction=65.0,
                renewable_share=15.0,
                population_millions=1200.0,
            ),
            Region(
                id="china_east_asia",
                name="China & East Asia",
                region_type=RegionType.EMERGING,
                gdp=110.0,
                emissions=140.0,
                vulnerability=35.0,
                adaptation_level=15.0,
                satisfaction=55.0,
                renewable_share=12.0,
                population_millions=2000.0,
            ),
            Region(
                id="south_asia_africa",
                name="South Asia & Africa",
                region_type=RegionType.DEVELOPING,
                gdp=60.0,
                emissions=40.0,
                vulnerability=75.0,
                adaptation_level=5.0,
                satisfaction=40.0,
                renewable_share=8.0,
                population_millions=3500.0,
            ),
            Region(
                id="latin_america_mideast",
                name="Latin America & Middle East",
                region_type=RegionType.EMERGING,
                gdp=80.0,
                emissions=70.0,
                vulnerability=50.0,
                adaptation_level=10.0,
                satisfaction=50.0,
                renewable_share=10.0,
                population_millions=1500.0,
            ),
            Region(
                id="pacific_islands",
                name="Pacific Island Nations",
                region_type=RegionType.SMALL_ISLAND,
                gdp=30.0,
                emissions=5.0,
                vulnerability=95.0,
                adaptation_level=2.0,
                satisfaction=30.0,
                renewable_share=20.0,
                population_millions=50.0,
            ),
        ]

    def generate_tipping_points(self) -> list:
        """Generate the 5 major climate tipping points."""
        return [
            TippingPoint(
                id="arctic_ice",
                name="Arctic Sea Ice Collapse",
                description=(
                    "Complete loss of summer Arctic sea ice, accelerating "
                    "warming through albedo feedback."
                ),
                threshold=1.5,
                risk_level=40.0,
                reversible=True,
            ),
            TippingPoint(
                id="amazon_dieback",
                name="Amazon Rainforest Dieback",
                description=(
                    "The Amazon transitions from carbon sink to carbon "
                    "source due to drought and deforestation."
                ),
                threshold=2.0,
                risk_level=25.0,
                reversible=False,
            ),
            TippingPoint(
                id="greenland_ice",
                name="Greenland Ice Sheet Collapse",
                description=(
                    "Irreversible melting of the Greenland ice sheet, "
                    "causing 7 meters of sea level rise over centuries."
                ),
                threshold=2.5,
                risk_level=15.0,
                reversible=False,
            ),
            TippingPoint(
                id="permafrost_thaw",
                name="Permafrost Carbon Release",
                description=(
                    "Widespread thawing of permafrost releases methane "
                    "and CO2, creating a positive feedback loop."
                ),
                threshold=2.0,
                risk_level=30.0,
                reversible=False,
            ),
            TippingPoint(
                id="coral_reef_die",
                name="Global Coral Reef Die-off",
                description=(
                    "Mass bleaching and death of coral reefs worldwide, "
                    "destroying marine biodiversity and coastal protection."
                ),
                threshold=1.5,
                risk_level=50.0,
                reversible=True,
            ),
        ]

    def generate_events(self) -> list:
        """Generate events spanning the 30-year council period."""
        return [
            # Years 1-5: Establishing authority
            YearlyEvent(
                year=1,
                title="Council Inauguration",
                description=(
                    "The Global Climate Council has been established with "
                    "you as chair. Initial assessments show global temperature "
                    "anomaly at 1.2C above pre-industrial levels. Major "
                    "decisions on emissions, energy policy, and adaptation "
                    "await. Fossil fuel lobbies are pushing for delay."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=3,
                title="First Tipping Point Warning",
                description=(
                    "Scientists report that Arctic sea ice is thinning "
                    "faster than models predicted. Coral reefs show mass "
                    "bleaching events across the Pacific. The scientific "
                    "community urges immediate action."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=5,
                title="Developing Nations Plea",
                description=(
                    "Pacific Island Nations and South Asian delegates "
                    "present evidence of rising seas, intensifying storms, "
                    "and crop failures. They demand adaptation funding "
                    "and accuse developed nations of climate colonialism."
                ),
                is_mandatory=True,
            ),
            # Years 6-10: Pressure mounts
            YearlyEvent(
                year=7,
                title="Fossil Fuel Industry Lobbying",
                description=(
                    "A coalition of fossil fuel companies offers to fund "
                    "council operations in exchange for delayed emissions "
                    "targets. The deal would boost GDP metrics significantly "
                    "but lock in fossil fuel dependency for decades."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=9,
                title="Climate Refugee Crisis",
                description=(
                    "Low-lying coastal areas experience severe flooding. "
                    "Millions displaced. Developing nations lack adaptation "
                    "infrastructure. International pressure to act intensifies."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=10,
                title="Geoengineering Proposal",
                description=(
                    "A tech consortium proposes stratospheric aerosol "
                    "injection to rapidly cool the planet. It promises "
                    "quick results but carries unknown risks to weather "
                    "patterns, agriculture, and ozone. Some scientists "
                    "support it; others call it reckless."
                ),
                is_mandatory=True,
            ),
            # Years 11-15: Critical decisions
            YearlyEvent(
                year=12,
                title="Emissions Data Controversy",
                description=(
                    "A leaked internal report shows emissions are 30% "
                    "higher than publicly reported figures. Publishing "
                    "accurate data would cause political upheaval and "
                    "economic panic, but suppressing it would betray "
                    "scientific integrity."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=14,
                title="Energy Transition Crossroads",
                description=(
                    "Renewable energy costs have dropped dramatically. "
                    "A full transition is technically feasible but would "
                    "cause short-term GDP loss and job displacement in "
                    "fossil fuel regions. Political approval would drop."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=15,
                title="Mid-Term Assessment",
                description=(
                    "Halfway through your tenure. Scientists present "
                    "updated projections showing the window for preventing "
                    "2C warming is closing rapidly. Every year of delay "
                    "makes the transition more expensive and risky."
                ),
                is_mandatory=True,
            ),
            # Years 16-20: Consequences emerge
            YearlyEvent(
                year=17,
                title="Food Security Crisis",
                description=(
                    "Climate-driven crop failures hit South Asia and "
                    "Africa hardest. Developed nations face price spikes "
                    "but not starvation. Equity in climate response "
                    "becomes a central issue."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=19,
                title="Tipping Point Cascade Warning",
                description=(
                    "Scientists warn that crossing one tipping point may "
                    "trigger others in a cascade effect. The permafrost "
                    "is showing accelerated thawing. The Amazon drought "
                    "cycle has intensified. Time is running short."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=20,
                title="Political Backlash",
                description=(
                    "Populist movements in developed nations push back "
                    "against climate policies, calling them economic "
                    "sabotage. Political approval for aggressive action "
                    "drops. Maintaining course requires courage."
                ),
                is_mandatory=True,
            ),
            # Years 21-25: Final window
            YearlyEvent(
                year=22,
                title="Breakthrough Technology",
                description=(
                    "A major carbon capture breakthrough makes negative "
                    "emissions technically feasible but requires massive "
                    "investment. Diverting funds from adaptation would "
                    "leave developing nations more vulnerable."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=24,
                title="Last Chance Summit",
                description=(
                    "Global leaders convene for a final climate summit. "
                    "The window for preventing catastrophic warming is "
                    "nearly closed. Your legacy as council chair depends "
                    "on the commitments made now."
                ),
                is_mandatory=True,
            ),
            # Years 26-30: Resolution
            YearlyEvent(
                year=26,
                title="Intergenerational Audit",
                description=(
                    "Youth representatives present a 'generational audit' "
                    "of council decisions. They evaluate whether today's "
                    "actions protect or burden future generations."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=28,
                title="Final Climate Assessment",
                description=(
                    "The comprehensive 30-year climate assessment is "
                    "prepared. Every policy decision, every delayed action, "
                    "every compromise is documented. The planet's trajectory "
                    "is clear."
                ),
                is_mandatory=True,
            ),
            YearlyEvent(
                year=30,
                title="Council Legacy Report",
                description=(
                    "Your 30-year tenure concludes. The legacy of your "
                    "leadership is measured not just in GDP and approval "
                    "ratings, but in the world you leave for the next "
                    "generation. Tipping points crossed or avoided, "
                    "nations helped or abandoned, science honored or "
                    "suppressed -- all are now part of the record."
                ),
                is_mandatory=True,
            ),
        ]

    def generate_council_state(self) -> CouncilState:
        """Generate initial council state."""
        return CouncilState()
