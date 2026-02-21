"""
Scenario generator for the Pandemic Grand Strategy simulation.

Creates the 8 countries, pathogen, vaccine candidates, pharma deals,
and monthly events. Deterministic given a seed.
"""

import random

from .models import (
    Country, GovernanceType, WealthTier, LockdownLevel,
    Pathogen, VaccineCandidate, VaccineStage,
    PharmaDeal, MonthlyEvent, GlobalState,
)


class ScenarioGenerator:
    """Generates the full scenario for a pandemic grand strategy run."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_countries(self) -> list:
        """Generate 8 countries with diverse profiles."""
        return [
            Country(
                id="norath",
                name="Norath",
                population=330_000_000,
                governance=GovernanceType.DEMOCRATIC,
                wealth=WealthTier.HIGH,
                gdp_billions=21000.0,
                healthcare_capacity=34,
                infected=500,
                reported_infections=500,
            ),
            Country(
                id="shenlan",
                name="Shenlan",
                population=1_400_000_000,
                governance=GovernanceType.AUTHORITARIAN,
                wealth=WealthTier.UPPER_MIDDLE,
                gdp_billions=14000.0,
                healthcare_capacity=18,
                infected=2000,
                reported_infections=800,  # underreporting
                compliance=85.0,
                public_trust=55.0,
            ),
            Country(
                id="valoria",
                name="Valoria",
                population=450_000_000,
                governance=GovernanceType.DEMOCRATIC,
                wealth=WealthTier.HIGH,
                gdp_billions=15000.0,
                healthcare_capacity=28,
                infected=1200,
                reported_infections=1200,
            ),
            Country(
                id="kembara",
                name="Kembara",
                population=280_000_000,
                governance=GovernanceType.DEMOCRATIC,
                wealth=WealthTier.LOWER_MIDDLE,
                gdp_billions=2700.0,
                healthcare_capacity=8,
                infected=300,
                reported_infections=300,
                poverty_rate=22.0,
                unemployment=8.0,
            ),
            Country(
                id="azania",
                name="Azania",
                population=1_200_000_000,
                governance=GovernanceType.HYBRID,
                wealth=WealthTier.LOW,
                gdp_billions=800.0,
                healthcare_capacity=3,
                infected=150,
                reported_infections=50,  # very limited testing
                poverty_rate=35.0,
                unemployment=12.0,
                public_trust=45.0,
            ),
            Country(
                id="meridia",
                name="Meridia",
                population=210_000_000,
                governance=GovernanceType.DEMOCRATIC,
                wealth=WealthTier.UPPER_MIDDLE,
                gdp_billions=1800.0,
                healthcare_capacity=12,
                infected=800,
                reported_infections=800,
                public_trust=55.0,
            ),
            Country(
                id="khorasan",
                name="Khorasan",
                population=85_000_000,
                governance=GovernanceType.AUTHORITARIAN,
                wealth=WealthTier.LOWER_MIDDLE,
                gdp_billions=600.0,
                healthcare_capacity=6,
                infected=400,
                reported_infections=100,  # heavy suppression
                compliance=75.0,
                public_trust=40.0,
            ),
            Country(
                id="insulara",
                name="Insulara",
                population=25_000_000,
                governance=GovernanceType.DEMOCRATIC,
                wealth=WealthTier.HIGH,
                gdp_billions=1400.0,
                healthcare_capacity=30,
                infected=50,
                reported_infections=50,
                public_trust=80.0,
                compliance=75.0,
            ),
        ]

    def generate_pathogen(self) -> Pathogen:
        """Generate the initial pathogen characteristics."""
        return Pathogen(
            name="ARIA-7",
            transmission_rate=2.5,
            fatality_rate=0.02,
            incubation_days=5,
        )

    def generate_vaccine_candidates(self) -> list:
        """Generate 3 vaccine candidates at different development stages."""
        return [
            VaccineCandidate(
                id="vax_alpha",
                name="CovaShield-A",
                manufacturer="NovaPharma",
                stage=VaccineStage.PHASE_2,
                efficacy=0.0,
                true_efficacy=0.88,
                safety_score=1.0,
                months_in_stage=1,
            ),
            VaccineCandidate(
                id="vax_beta",
                name="mRNA-Rapid",
                manufacturer="GeneCure",
                stage=VaccineStage.PHASE_1,
                efficacy=0.0,
                true_efficacy=0.94,
                safety_score=0.95,
                months_in_stage=0,
            ),
            VaccineCandidate(
                id="vax_gamma",
                name="TradiVax",
                manufacturer="BioStandard",
                stage=VaccineStage.PRECLINICAL,
                efficacy=0.0,
                true_efficacy=0.72,
                safety_score=1.0,
                months_in_stage=0,
            ),
        ]

    def generate_pharma_deals(self) -> list:
        """Generate pharmaceutical company deal offers."""
        return [
            PharmaDeal(
                id="deal_nova_exclusive",
                pharma_name="NovaPharma",
                vaccine_id="vax_alpha",
                offer_description=(
                    "NovaPharma offers exclusive distribution rights for "
                    "CovaShield-A. In exchange for prioritizing wealthy nations "
                    "(Norath, Valoria, Insulara), they guarantee 500M doses at "
                    "$28/dose and a $5M 'consulting fee' to WHO leadership."
                ),
                exclusive=True,
                kickback_amount=5_000_000,
                price_per_dose=28.0,
                doses_promised=500_000_000,
                priority_countries=["norath", "valoria", "insulara"],
                month_available=4,
            ),
            PharmaDeal(
                id="deal_genecure_fast",
                pharma_name="GeneCure",
                vaccine_id="vax_beta",
                offer_description=(
                    "GeneCure proposes fast-tracking mRNA-Rapid through Phase 3 "
                    "trials, skipping the 6-month safety monitoring window. "
                    "They claim the technology is proven. In return, they want "
                    "WHO endorsement and a $3M 'research partnership' payment."
                ),
                exclusive=False,
                kickback_amount=3_000_000,
                price_per_dose=38.0,
                doses_promised=300_000_000,
                priority_countries=[],
                month_available=6,
            ),
            PharmaDeal(
                id="deal_biostandard_cheap",
                pharma_name="BioStandard",
                vaccine_id="vax_gamma",
                offer_description=(
                    "BioStandard offers TradiVax at $4/dose for all countries. "
                    "No exclusive deals, no kickbacks. But their vaccine is "
                    "slower to develop and has lower efficacy. They request "
                    "$200M in development funding from the global fund."
                ),
                exclusive=False,
                kickback_amount=0,
                price_per_dose=4.0,
                doses_promised=2_000_000_000,
                priority_countries=[],
                month_available=8,
            ),
            PharmaDeal(
                id="deal_nova_booster",
                pharma_name="NovaPharma",
                vaccine_id="vax_alpha",
                offer_description=(
                    "NovaPharma's second offer: supply booster doses exclusively "
                    "to countries that accepted the original deal. A $2M annual "
                    "'advisory board' position for WHO leadership is included."
                ),
                exclusive=True,
                kickback_amount=2_000_000,
                price_per_dose=35.0,
                doses_promised=200_000_000,
                priority_countries=["norath", "valoria", "insulara"],
                month_available=14,
            ),
        ]

    def generate_monthly_events(self) -> list:
        """Generate events spanning the 24-month timeline."""
        return [
            # Month 1-3: Outbreak emerges
            MonthlyEvent(
                month=1,
                title="Novel Pathogen Identified",
                description=(
                    "ARIA-7, a novel respiratory pathogen, has been identified "
                    "in multiple countries simultaneously. Initial R0 estimated "
                    "at 2.5 with a 2% fatality rate. The world looks to the WHO "
                    "for leadership."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=2,
                title="Exponential Growth Phase",
                description=(
                    "Cases are doubling every 10 days across all 8 nations. "
                    "Hospitals in Azania and Khorasan are already strained. "
                    "Wealthy nations are stockpiling PPE and ventilators."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=3,
                title="Global Panic Begins",
                description=(
                    "Stock markets crash 15%. Social media is flooded with "
                    "misinformation about miracle cures. Several countries "
                    "are implementing uncoordinated border closures."
                ),
            ),
            # Month 4-6: First wave peaks
            MonthlyEvent(
                month=4,
                title="First Wave Peak",
                description=(
                    "Infections peak in wealthy nations with better testing. "
                    "NovaPharma approaches WHO with an exclusive vaccine deal. "
                    "Poor nations report suspiciously low case numbers."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=5,
                title="Healthcare System Collapse in Azania",
                description=(
                    "Azania's healthcare system is overwhelmed. Makeshift "
                    "hospitals in parking lots. Mortality rate is 3x higher "
                    "than wealthy nations due to lack of ventilators and ICU beds."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=6,
                title="Variant Alpha Emerges",
                description=(
                    "A new variant with 40% higher transmissibility is detected "
                    "in Meridia. Current vaccine candidates may have reduced "
                    "efficacy. GeneCure proposes fast-tracking mRNA-Rapid."
                ),
                is_mandatory=True,
            ),
            # Month 7-9: Vaccine race
            MonthlyEvent(
                month=7,
                title="Vaccine Nationalism",
                description=(
                    "Norath and Valoria have pre-purchased 80% of NovaPharma's "
                    "initial production run. Poor nations are at the back of "
                    "the queue. Global criticism mounts."
                ),
            ),
            MonthlyEvent(
                month=8,
                title="Anti-Lockdown Protests",
                description=(
                    "Massive protests erupt in Norath and Valoria against "
                    "lockdown measures. Kembara reports rising hunger as "
                    "informal workers lose income. Civil liberties groups "
                    "challenge military-enforced lockdowns in Khorasan."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=9,
                title="Vaccine Approval Race",
                description=(
                    "CovaShield-A is nearing Phase 3 completion. Political "
                    "pressure to approve before full safety data is available. "
                    "Each week of delay means thousands more deaths."
                ),
            ),
            # Month 10-12: Distribution chaos
            MonthlyEvent(
                month=10,
                title="First Vaccines Available",
                description=(
                    "Initial vaccine doses are being produced. The critical "
                    "question: who gets them first? Wealthy nations are "
                    "offering to pay 5x the price. Healthcare workers and "
                    "elderly everywhere need protection."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=11,
                title="Cold Chain Crisis",
                description=(
                    "mRNA vaccines require -70C storage. Azania and Kembara "
                    "lack the infrastructure. Only the traditional vaccine "
                    "candidate can be distributed in hot climates without "
                    "specialized equipment."
                ),
            ),
            MonthlyEvent(
                month=12,
                title="One Year Anniversary",
                description=(
                    "One year into the pandemic. The world is exhausted. "
                    "Economic damage is severe. Vaccine rollout is uneven. "
                    "A moment of global reckoning."
                ),
                is_mandatory=True,
            ),
            # Month 13-15: Mid-pandemic fatigue
            MonthlyEvent(
                month=13,
                title="Variant Beta Emerges",
                description=(
                    "A more severe variant emerges in an under-vaccinated "
                    "region. Partially evades vaccine immunity. Scientists "
                    "warn that allowing the virus to spread unchecked in "
                    "poor nations creates variant factories."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=14,
                title="Pandemic Fatigue",
                description=(
                    "Compliance is dropping everywhere. People are ignoring "
                    "lockdown orders. Businesses are reopening without "
                    "authorization. Mental health crisis deepens."
                ),
            ),
            MonthlyEvent(
                month=15,
                title="Elderly Sacrifice Debate",
                description=(
                    "Some advisors argue for 'focused protection' — letting "
                    "the virus spread among young/healthy while shielding the "
                    "elderly. Critics call it 'sacrificing grandparents for GDP.'"
                ),
                is_mandatory=True,
            ),
            # Month 16-18: Recovery begins
            MonthlyEvent(
                month=16,
                title="Manufacturing Scale-Up",
                description=(
                    "Vaccine production is ramping up. 2 billion doses "
                    "projected by end of month 18. But distribution to "
                    "remote and poor areas remains a challenge."
                ),
            ),
            MonthlyEvent(
                month=17,
                title="Misinformation Surge",
                description=(
                    "Anti-vaccine movements gain traction globally. "
                    "Conspiracy theories about WHO, Big Pharma, and "
                    "government control spread rapidly. Trust in institutions "
                    "erodes."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=18,
                title="Economic Recovery Pressure",
                description=(
                    "G20 nations push for rapid reopening regardless of "
                    "vaccination rates in poorer nations. 'We can't wait "
                    "for everyone' becomes the rallying cry."
                ),
            ),
            # Month 19-21: Late-stage decisions
            MonthlyEvent(
                month=19,
                title="Variant Gamma Emerges",
                description=(
                    "A third variant with immune escape properties. Booster "
                    "doses become critical. The divide between vaccinated "
                    "and unvaccinated nations deepens."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=20,
                title="Patent Waiver Debate",
                description=(
                    "Low-income nations demand a TRIPS waiver to manufacture "
                    "generic vaccines. Pharma companies threaten to reduce "
                    "future R&D investment if patents are waived."
                ),
            ),
            MonthlyEvent(
                month=21,
                title="Long COVID Crisis",
                description=(
                    "Long-term health effects emerge in millions of recovered "
                    "patients. Healthcare systems face a second, slower crisis "
                    "of chronic illness."
                ),
            ),
            # Month 22-24: Endgame
            MonthlyEvent(
                month=22,
                title="Endemic Transition Debate",
                description=(
                    "Some nations declare the pandemic 'over' and drop all "
                    "measures. Others argue it's premature. The WHO must "
                    "decide on a unified recommendation."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=23,
                title="Accountability Hearings",
                description=(
                    "International media begins investigating WHO decision-"
                    "making. Questions about vaccine equity, pharma deals, "
                    "and data transparency are raised."
                ),
                is_mandatory=True,
            ),
            MonthlyEvent(
                month=24,
                title="Final Assessment",
                description=(
                    "The 24-month pandemic response period concludes. "
                    "History will judge the decisions made. How many died "
                    "who didn't have to? Was the response equitable? "
                    "Were civil liberties respected?"
                ),
                is_mandatory=True,
            ),
        ]

    def generate_global_state(self) -> GlobalState:
        """Generate initial global state."""
        return GlobalState()
