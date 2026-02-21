"""
Scenario generator for the Intelligence Mosaic simulation.

Creates intelligence reports from 4 source types, 6 cases under investigation,
4 policymakers with different agendas, and peer analysts who may dissent.
Deterministic given a seed.
"""

import random

from .models import (
    AnalystState, Case, CasePriority, CaseStatus, ClassificationLevel,
    ConfidenceLevel, IntelReport, Policymaker, PolicymakerAgenda,
    PeerAnalyst, SourceReliability, SourceType,
)


class ScenarioGenerator:
    """Generates the full scenario for an Intelligence Mosaic simulation run."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def generate_reports(self) -> list:
        """Generate 20 intelligence reports from 4 source types."""
        reports = [
            # --- HUMINT (5 reports) ---
            IntelReport(
                id="rpt_humint_01",
                source_type=SourceType.HUMINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.SECRET,
                title="Agent CARDINAL: Weapons Transfer",
                summary=(
                    "Longstanding asset reports convoy of military vehicles "
                    "moving north from Region Alpha. Claims 12 vehicles carrying "
                    "surface-to-air missile components. Timing correlates with "
                    "increased chatter on military frequencies."
                ),
                case_ids=["case_01", "case_03"],
                day_available=1,
                supports_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_humint_02",
                source_type=SourceType.HUMINT,
                reliability=SourceReliability.D,
                original_reliability=SourceReliability.D,
                classification=ClassificationLevel.SECRET,
                title="Walk-In Source: Nuclear Facility",
                summary=(
                    "Unvetted walk-in claims underground nuclear enrichment facility "
                    "operating in the eastern province. Provides hand-drawn map and "
                    "descriptions of centrifuge operations. Cannot provide physical "
                    "evidence. Motivation: asylum in exchange for information."
                ),
                case_ids=["case_02"],
                day_available=3,
                is_fabricated=True,
                supports_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_humint_03",
                source_type=SourceType.HUMINT,
                reliability=SourceReliability.A,
                original_reliability=SourceReliability.A,
                classification=ClassificationLevel.SCI,
                title="Agent RAVEN: Peace Negotiations",
                summary=(
                    "Senior diplomatic source confirms back-channel peace talks "
                    "between parties. Foreign minister privately willing to accept "
                    "ceasefire terms. Military leadership divided. Key condition: "
                    "no public humiliation."
                ),
                case_ids=["case_04", "case_06"],
                day_available=5,
                supports_narrative="dovish",
                contradicts_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_humint_04",
                source_type=SourceType.HUMINT,
                reliability=SourceReliability.C,
                original_reliability=SourceReliability.C,
                classification=ClassificationLevel.SECRET,
                title="Informant LOTUS: Training Camps",
                summary=(
                    "Regional informant reports three new training camps in the "
                    "border zone. Estimates 200-300 fighters. Notes foreign "
                    "instructors present. However, same informant previously "
                    "exaggerated numbers by 3x on two occasions."
                ),
                case_ids=["case_01", "case_05"],
                day_available=8,
                supports_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_humint_05",
                source_type=SourceType.HUMINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.TOP_SECRET,
                title="Agent SHADOW: Disinformation Campaign",
                summary=(
                    "Trusted asset within foreign intelligence service reveals "
                    "active disinformation operation. Enemy planting false intelligence "
                    "about WMD programs to provoke overreaction. Specifically mentions "
                    "fabricated walk-in sources."
                ),
                case_ids=["case_02", "case_06"],
                day_available=12,
                contradicts_narrative="hawkish",
            ),

            # --- SIGINT (5 reports) ---
            IntelReport(
                id="rpt_sigint_01",
                source_type=SourceType.SIGINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.TOP_SECRET,
                title="Intercepted Military Communications",
                summary=(
                    "Intercepts show increased encrypted communications between "
                    "military HQ and forward bases. Pattern consistent with "
                    "pre-deployment activity. Volume up 340% from baseline."
                ),
                case_ids=["case_01", "case_03"],
                day_available=2,
                supports_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_sigint_02",
                source_type=SourceType.SIGINT,
                reliability=SourceReliability.A,
                original_reliability=SourceReliability.A,
                classification=ClassificationLevel.SCI,
                title="Diplomatic Cable Intercepts",
                summary=(
                    "Decrypted diplomatic traffic reveals foreign government "
                    "internally debating ceasefire proposal. Ambassador instructed "
                    "to stall publicly while back-channel continues. Key phrase: "
                    "'We need 14 days to bring the generals around.'"
                ),
                case_ids=["case_04"],
                day_available=7,
                supports_narrative="dovish",
            ),
            IntelReport(
                id="rpt_sigint_03",
                source_type=SourceType.SIGINT,
                reliability=SourceReliability.C,
                original_reliability=SourceReliability.C,
                classification=ClassificationLevel.SECRET,
                title="Financial Wire Transfers",
                summary=(
                    "Monitored financial channels show series of transfers from "
                    "state accounts to shell companies. Pattern suggests arms "
                    "procurement. Total value: approximately $47M over 90 days."
                ),
                case_ids=["case_03", "case_05"],
                day_available=10,
            ),
            IntelReport(
                id="rpt_sigint_04",
                source_type=SourceType.SIGINT,
                reliability=SourceReliability.E,
                original_reliability=SourceReliability.E,
                classification=ClassificationLevel.SECRET,
                title="Unverified Communication Intercept",
                summary=(
                    "Single intercept of conversation between unidentified speakers "
                    "referencing 'the shipment' and 'the facility in the east.' "
                    "Audio quality poor. Could be commercial, military, or civilian "
                    "context. Translation uncertain."
                ),
                case_ids=["case_02"],
                day_available=4,
                is_fabricated=False,  # Not fabricated but unreliable
            ),
            IntelReport(
                id="rpt_sigint_05",
                source_type=SourceType.SIGINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.TOP_SECRET,
                title="Cyber Activity Analysis",
                summary=(
                    "Significant increase in state-sponsored cyber probing of "
                    "critical infrastructure. 17 unique attack vectors identified. "
                    "Pattern consistent with pre-conflict preparation but could also "
                    "indicate intelligence gathering only."
                ),
                case_ids=["case_05", "case_06"],
                day_available=15,
            ),

            # --- IMINT (5 reports) ---
            IntelReport(
                id="rpt_imint_01",
                source_type=SourceType.IMINT,
                reliability=SourceReliability.A,
                original_reliability=SourceReliability.A,
                classification=ClassificationLevel.SECRET,
                title="Satellite Imagery: Vehicle Movement",
                summary=(
                    "High-resolution satellite imagery confirms 8-12 military "
                    "vehicles at staging area in Region Alpha. Vehicle types "
                    "consistent with logistics/transport. No weapons systems "
                    "visible in current imagery."
                ),
                case_ids=["case_01"],
                day_available=2,
                contradicts_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_imint_02",
                source_type=SourceType.IMINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.TOP_SECRET,
                title="Aerial Reconnaissance: Eastern Province",
                summary=(
                    "Drone imagery of suspected nuclear site shows construction "
                    "activity. Buildings consistent with industrial facility but "
                    "could be agricultural processing. No observable radiation "
                    "signatures. Ground truth needed."
                ),
                case_ids=["case_02"],
                day_available=6,
            ),
            IntelReport(
                id="rpt_imint_03",
                source_type=SourceType.IMINT,
                reliability=SourceReliability.A,
                original_reliability=SourceReliability.A,
                classification=ClassificationLevel.SECRET,
                title="Port Activity Monitoring",
                summary=(
                    "Commercial satellite shows unusual port activity. Three "
                    "cargo vessels with known arms-trade registry docked "
                    "simultaneously. Containers offloaded to military trucks. "
                    "Photographic evidence clear and timestamped."
                ),
                case_ids=["case_03"],
                day_available=11,
                supports_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_imint_04",
                source_type=SourceType.IMINT,
                reliability=SourceReliability.C,
                original_reliability=SourceReliability.C,
                classification=ClassificationLevel.CONFIDENTIAL,
                title="Border Camp Imagery",
                summary=(
                    "Imagery of border area shows temporary structures consistent "
                    "with training camps OR refugee displacement. Seasonal patterns "
                    "make determination difficult. Population count estimate: "
                    "100-400 individuals."
                ),
                case_ids=["case_05"],
                day_available=9,
            ),
            IntelReport(
                id="rpt_imint_05",
                source_type=SourceType.IMINT,
                reliability=SourceReliability.F,
                original_reliability=SourceReliability.F,
                classification=ClassificationLevel.SECRET,
                title="Historical Comparison Analysis",
                summary=(
                    "Comparison of current imagery with 2003 pre-invasion imagery "
                    "from analogous situation. Analyst notes 'striking similarities' "
                    "in staging patterns. Note: This is pattern-matching, not "
                    "direct evidence. Confirmation bias risk flagged."
                ),
                case_ids=["case_01", "case_06"],
                day_available=14,
            ),

            # --- OSINT (5 reports) ---
            IntelReport(
                id="rpt_osint_01",
                source_type=SourceType.OSINT,
                reliability=SourceReliability.C,
                original_reliability=SourceReliability.C,
                classification=ClassificationLevel.UNCLASSIFIED,
                title="Social Media Activity Analysis",
                summary=(
                    "Surge in military-related social media posts from Region Alpha. "
                    "Multiple accounts posting photos of military vehicles. Some "
                    "accounts appear to be bot-generated. Genuine activity mixed with "
                    "possible information operations."
                ),
                case_ids=["case_01", "case_06"],
                day_available=1,
            ),
            IntelReport(
                id="rpt_osint_02",
                source_type=SourceType.OSINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.UNCLASSIFIED,
                title="Academic Research: Regional Stability",
                summary=(
                    "Published think-tank analysis concludes that current tensions "
                    "are primarily driven by domestic politics on both sides. "
                    "Authors argue military posturing is for internal consumption, "
                    "not actual war preparation. Peer-reviewed."
                ),
                case_ids=["case_04", "case_06"],
                day_available=4,
                supports_narrative="dovish",
                contradicts_narrative="hawkish",
            ),
            IntelReport(
                id="rpt_osint_03",
                source_type=SourceType.OSINT,
                reliability=SourceReliability.D,
                original_reliability=SourceReliability.D,
                classification=ClassificationLevel.UNCLASSIFIED,
                title="News Report: Arms Deal",
                summary=(
                    "Regional news outlet reports major arms deal between "
                    "subject nation and foreign supplier. Details unconfirmed. "
                    "News outlet has history of being used for government "
                    "propaganda. Could be deliberate leak or planted story."
                ),
                case_ids=["case_03"],
                day_available=13,
            ),
            IntelReport(
                id="rpt_osint_04",
                source_type=SourceType.OSINT,
                reliability=SourceReliability.A,
                original_reliability=SourceReliability.A,
                classification=ClassificationLevel.UNCLASSIFIED,
                title="Commercial Shipping Data",
                summary=(
                    "Automated tracking of commercial shipping shows 40% decline "
                    "in civilian port activity at three major harbors. Consistent "
                    "with military commandeering of port facilities. Data from "
                    "verified commercial tracking services."
                ),
                case_ids=["case_03", "case_01"],
                day_available=16,
            ),
            IntelReport(
                id="rpt_osint_05",
                source_type=SourceType.OSINT,
                reliability=SourceReliability.B,
                original_reliability=SourceReliability.B,
                classification=ClassificationLevel.UNCLASSIFIED,
                title="NGO Field Report: Civilian Displacement",
                summary=(
                    "International humanitarian organization reports increasing "
                    "civilian displacement from border regions. 15,000+ refugees "
                    "in past 30 days. Locals cite fear of military operations. "
                    "Consistent with pre-conflict indicators."
                ),
                case_ids=["case_05", "case_04"],
                day_available=18,
            ),
        ]
        return reports

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------

    def generate_cases(self) -> list:
        """Generate 6 ongoing investigation cases requiring assessment."""
        return [
            Case(
                id="case_01",
                title="OPERATION IRON VEIL: Military Mobilization Assessment",
                description=(
                    "Assess whether observed military movements in Region Alpha "
                    "represent genuine offensive preparation or routine exercises. "
                    "Multiple sources disagree. Policymakers want definitive answer."
                ),
                priority=CasePriority.CRITICAL,
                report_ids=["rpt_humint_01", "rpt_sigint_01", "rpt_imint_01",
                             "rpt_osint_01", "rpt_humint_04", "rpt_imint_05",
                             "rpt_osint_04"],
                dissenting_analysts=["analyst_chen"],
                deadline_day=10,
                historical_analog="2003 Iraq WMD assessment — pattern matching risk",
            ),
            Case(
                id="case_02",
                title="LOOKING GLASS: Nuclear Facility Intelligence",
                description=(
                    "Evaluate credibility of walk-in source claiming underground "
                    "nuclear enrichment facility. Walk-in intelligence conflicts "
                    "with signals intelligence and imagery analysis. High political "
                    "sensitivity."
                ),
                priority=CasePriority.CRITICAL,
                report_ids=["rpt_humint_02", "rpt_sigint_04", "rpt_imint_02",
                             "rpt_humint_05"],
                dissenting_analysts=["analyst_chen", "analyst_okonkwo"],
                deadline_day=15,
                historical_analog="Curveball / Iraq WMD fabrication precedent",
            ),
            Case(
                id="case_03",
                title="TRADE WINDS: Arms Procurement Network",
                description=(
                    "Map and assess the scope of the subject nation's arms "
                    "procurement network. Multiple intelligence streams provide "
                    "pieces but full picture unclear. Financial intelligence "
                    "suggests significant expenditure."
                ),
                priority=CasePriority.HIGH,
                report_ids=["rpt_humint_01", "rpt_sigint_01", "rpt_sigint_03",
                             "rpt_imint_03", "rpt_osint_03"],
                dissenting_analysts=["analyst_park"],
                deadline_day=20,
            ),
            Case(
                id="case_04",
                title="OLIVE BRANCH: Diplomatic Initiative Assessment",
                description=(
                    "Evaluate the credibility and prospects of back-channel peace "
                    "negotiations. Some intelligence suggests genuine willingness "
                    "to negotiate; other indicators point to stalling tactics."
                ),
                priority=CasePriority.HIGH,
                report_ids=["rpt_humint_03", "rpt_sigint_02", "rpt_osint_02",
                             "rpt_osint_05"],
                dissenting_analysts=["analyst_volkov"],
                deadline_day=22,
            ),
            Case(
                id="case_05",
                title="GREY ZONE: Border Security Threat",
                description=(
                    "Assess the nature and scale of activity in the border zone. "
                    "Could be training camps, refugee displacement, or smuggling "
                    "operations. Ground truth limited. Imagery ambiguous."
                ),
                priority=CasePriority.MEDIUM,
                report_ids=["rpt_humint_04", "rpt_sigint_03", "rpt_imint_04",
                             "rpt_sigint_05", "rpt_osint_05"],
                dissenting_analysts=["analyst_okonkwo"],
                deadline_day=25,
            ),
            Case(
                id="case_06",
                title="MOSAIC: Strategic Intent Assessment",
                description=(
                    "Overarching assessment of subject nation's strategic intent. "
                    "Synthesize all intelligence streams to determine: Is the "
                    "subject nation preparing for war, engaging in deterrence "
                    "posturing, or genuinely seeking peace? This is the assessment "
                    "that goes to the President."
                ),
                priority=CasePriority.CRITICAL,
                report_ids=["rpt_humint_03", "rpt_humint_05", "rpt_sigint_05",
                             "rpt_imint_05", "rpt_osint_01", "rpt_osint_02"],
                dissenting_analysts=["analyst_chen", "analyst_volkov"],
                deadline_day=28,
                historical_analog="NIE 2002 / groupthink risk",
            ),
        ]

    # ------------------------------------------------------------------
    # Policymakers
    # ------------------------------------------------------------------

    def generate_policymakers(self) -> list:
        """Generate 4 policymakers with different agendas."""
        return [
            Policymaker(
                id="pm_sec_defense",
                name="Secretary Margaret Thornton",
                title="Secretary of Defense",
                agenda=PolicymakerAgenda.HAWKISH,
                preferred_conclusion=(
                    "The subject nation is actively preparing for military "
                    "aggression. Immediate defensive measures required."
                ),
                description=(
                    "Career defense hawk. Wants intelligence that justifies "
                    "increased military posture. Has publicly stated the threat "
                    "is 'clear and present.' Will be unhappy with ambiguous findings."
                ),
            ),
            Policymaker(
                id="pm_sec_state",
                name="Secretary James Callahan",
                title="Secretary of State",
                agenda=PolicymakerAgenda.DOVISH,
                preferred_conclusion=(
                    "Diplomatic channels remain viable. The subject nation's "
                    "posturing is primarily defensive and for domestic consumption."
                ),
                description=(
                    "Veteran diplomat. Personally invested in back-channel talks. "
                    "Wants intelligence showing negotiations can succeed. May "
                    "downplay military indicators that threaten his diplomatic track."
                ),
            ),
            Policymaker(
                id="pm_nsa",
                name="Dr. Patricia Reeves",
                title="National Security Advisor",
                agenda=PolicymakerAgenda.POLITICAL,
                preferred_conclusion=(
                    "Whatever conclusion best supports the administration's "
                    "public messaging. Currently: 'We are managing the situation "
                    "through strength and diplomacy.'"
                ),
                description=(
                    "Political operator first, policy expert second. Wants "
                    "intelligence that won't embarrass the President before "
                    "midterm elections. Will pressure for conclusions that align "
                    "with the news cycle."
                ),
            ),
            Policymaker(
                id="pm_dni",
                name="Director Robert Nakamura",
                title="Director of National Intelligence",
                agenda=PolicymakerAgenda.ANALYTICAL,
                preferred_conclusion=(
                    "An honest, well-sourced assessment regardless of political "
                    "implications. The analytic product must be defensible."
                ),
                description=(
                    "Former career analyst. Believes in analytic integrity above "
                    "all. The only policymaker who genuinely wants the truth, "
                    "even if it is inconvenient. Will defend analysts who resist "
                    "political pressure."
                ),
            ),
        ]

    # ------------------------------------------------------------------
    # Peer Analysts
    # ------------------------------------------------------------------

    def generate_peer_analysts(self) -> list:
        """Generate peer analysts who may dissent or agree."""
        return [
            PeerAnalyst(
                id="analyst_chen",
                name="Dr. Lisa Chen",
                specialty="Military Analysis / Order of Battle",
                dissents_on=["case_01", "case_02", "case_06"],
                dissent_text=(
                    "Current military activity is consistent with biannual "
                    "exercises, not offensive preparation. Satellite imagery shows "
                    "logistics vehicles, not weapons platforms. Walk-in source on "
                    "nuclear facility shows classic fabrication indicators."
                ),
                description=(
                    "20-year veteran analyst. Expert on the region's military. "
                    "Known for cautious assessments. Was right about Iraq in 2003 "
                    "when the consensus was wrong."
                ),
            ),
            PeerAnalyst(
                id="analyst_okonkwo",
                name="Michael Okonkwo",
                specialty="WMD / Proliferation Analysis",
                dissents_on=["case_02", "case_05"],
                dissent_text=(
                    "Walk-in source assessment lacks corroboration. IMINT of "
                    "eastern facility is ambiguous at best. Recommend LOW confidence "
                    "pending ground verification. Border activity more consistent "
                    "with refugee displacement than military training."
                ),
                description=(
                    "Specialist in WMD intelligence. Meticulous about source "
                    "validation. Still bitter about the 2003 failures. Will not "
                    "sign off on thin evidence."
                ),
            ),
            PeerAnalyst(
                id="analyst_park",
                name="Captain James Park",
                specialty="Financial Intelligence / Arms Trafficking",
                dissents_on=["case_03"],
                dissent_text=(
                    "Financial patterns suggest procurement activity, but the "
                    "specific weapons systems implied by other reporting cannot be "
                    "confirmed through financial channels alone. Some transfers "
                    "may be legitimate trade."
                ),
                description=(
                    "Former military intelligence officer. Strong on financial "
                    "analysis. Careful about not over-interpreting money flows. "
                    "Respected but not politically connected."
                ),
            ),
            PeerAnalyst(
                id="analyst_volkov",
                name="Dr. Anna Volkov",
                specialty="Political Analysis / Diplomatic Intelligence",
                dissents_on=["case_04", "case_06"],
                dissent_text=(
                    "Back-channel peace talks may be a stalling tactic to buy "
                    "time for military preparation. Historical precedent suggests "
                    "dual-track approach common for this actor. Cannot rule out "
                    "genuine diplomatic intent, but skepticism warranted."
                ),
                description=(
                    "Regional political expert. PhD in international relations. "
                    "Distrusts the subject nation based on historical pattern. "
                    "Her skepticism is well-founded but could shade toward bias."
                ),
            ),
        ]

    # ------------------------------------------------------------------
    # Initial analyst state
    # ------------------------------------------------------------------

    def generate_analyst_state(self) -> AnalystState:
        """Generate initial analyst state."""
        return AnalystState()

    # ------------------------------------------------------------------
    # Full generation
    # ------------------------------------------------------------------

    def generate_all(self):
        """Generate all scenario components."""
        return {
            "reports": self.generate_reports(),
            "cases": self.generate_cases(),
            "policymakers": self.generate_policymakers(),
            "peer_analysts": self.generate_peer_analysts(),
            "analyst_state": self.generate_analyst_state(),
        }
