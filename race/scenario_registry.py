"""Central metadata registry for all supported simulations."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScenarioSpec:
    simulation_id: str
    display_name: str
    duration_arg: str
    duration_label: str
    default_duration: int
    prompt_code: Optional[str] = None
    cli_code: Optional[str] = None


SCENARIOS: tuple[ScenarioSpec, ...] = (
    ScenarioSpec("vending_machine", "VENDING MACHINE", "days", "Days", 90, None),
    ScenarioSpec("prisoners_dilemma", "PRISONER'S DILEMMA", "rounds", "Rounds", 100, "ipd", "pd"),
    ScenarioSpec("emergency_room", "EMERGENCY ROOM", "hours", "Hours", 72, "er"),
    ScenarioSpec("whistleblower", "CORPORATE WHISTLEBLOWER", "weeks", "Weeks", 8, "wb"),
    ScenarioSpec("content_moderator", "CONTENT MODERATOR", "hours", "Hours", 48, "cm"),
    ScenarioSpec("rules_of_engagement", "RULES OF ENGAGEMENT", "hours", "Hours", 72, "roe"),
    ScenarioSpec("reputation_economy", "REPUTATION ECONOMY", "days", "Days", 60, "re"),
    ScenarioSpec("drug_pricing", "DRUG PRICING ARCHITECT", "quarters", "Quarters", 12, "dp"),
    ScenarioSpec("mayor_splitsville", "MAYOR OF SPLITSVILLE", "months", "Months", 24, "ms"),
    ScenarioSpec("auction_house", "AUCTION HOUSE", "sessions", "Sessions", 10, "ah"),
    ScenarioSpec("poker_tournament", "POKER INTELLIGENCE", "hands", "Hands", 20, "pt"),
    ScenarioSpec("resource_commons", "RESOURCE COMMONS", "seasons", "Seasons", 30, "rc"),
    ScenarioSpec("supply_chain", "SUPPLY CHAIN DOMINOS", "weeks", "Weeks", 52, "sc"),
    ScenarioSpec("pandemic_ward", "PANDEMIC WARD ZERO", "days", "Days", 90, "pw"),
    ScenarioSpec("asteroid_defense", "ASTEROID DEFENSE COORDINATOR", "months", "Months", 24, "ad"),
    ScenarioSpec("species_triage", "SPECIES TRIAGE OFFICER", "quarters", "Quarters", 40, "st"),
    ScenarioSpec("nuclear_launch", "NUCLEAR LAUNCH AUTHORITY", "hours", "Hours", 24, "nl"),
    ScenarioSpec("news_editor", "NEWS EDITOR UNDER FIRE", "hours", "Hours", 48, "ne"),
    ScenarioSpec("last_restaurant", "LAST RESTAURANT STANDING", "weeks", "Weeks", 52, "lr"),
    ScenarioSpec("flash_crash", "FLASH CRASH TRADER", "hours", "Hours", 120, "fc"),
    ScenarioSpec("startup_founder", "STARTUP FOUNDER GAUNTLET", "months", "Months", 24, "sf"),
    ScenarioSpec("real_estate", "REAL ESTATE EMPIRE", "months", "Months", 36, "re2"),
    ScenarioSpec("organ_allocation", "ORGAN ALLOCATION BOARD", "weeks", "Weeks", 52, "oa"),
    ScenarioSpec("experimental_treatment", "EXPERIMENTAL TREATMENT TRIBUNAL", "months", "Months", 18, "et"),
    ScenarioSpec("pandemic_grand", "PANDEMIC GRAND STRATEGY", "months", "Months", 24, "pg"),
    ScenarioSpec("drone_strike", "DRONE STRIKE AUTHORIZATION", "hours", "Hours", 48, "ds"),
    ScenarioSpec("intelligence_mosaic", "INTELLIGENCE MOSAIC", "days", "Days", 30, "im"),
    ScenarioSpec("pow_camp", "POW CAMP COMMANDER", "weeks", "Weeks", 52, "pc"),
    ScenarioSpec("trolley_problem", "TROLLEY PROBLEMS AT SCALE", "rounds", "Rounds", 100, "tp"),
    ScenarioSpec("privacy_security", "PRIVACY VS. SECURITY TRIBUNAL", "days", "Days", 90, "ps"),
    ScenarioSpec("school_principal", "SCHOOL PRINCIPAL IN CRISIS", "weeks", "Weeks", 52, "sp"),
    ScenarioSpec("hostage_negotiator", "HOSTAGE NEGOTIATOR", "hours", "Hours", 72, "hn"),
    ScenarioSpec("hr_ethics", "HR ETHICS TRIBUNAL", "days", "Days", 90, "hr"),
    ScenarioSpec("bug_bounty", "BUG BOUNTY BATTLEFIELD", "days", "Days", 90, "bb"),
    ScenarioSpec("infrastructure_siege", "INFRASTRUCTURE UNDER SIEGE", "hours", "Hours", 72, "is"),
    ScenarioSpec("space_mission", "SPACE MISSION CONTROL", "days", "Days", 90, "sm"),
    ScenarioSpec("climate_tipping", "CLIMATE TIPPING POINT COUNCIL", "years", "Years", 30, "ct"),
    ScenarioSpec("ai_containment", "AI CONTAINMENT PROTOCOL", "days", "Days", 90, "ac"),
    ScenarioSpec("ecosystem_collapse", "ECOSYSTEM COLLAPSE MANAGER", "months", "Months", 24, "ec"),
    ScenarioSpec("pollution_prosperity", "POLLUTION VS. PROSPERITY", "years", "Years", 20, "pp"),
    ScenarioSpec("geoengineering", "GEOENGINEERING GOVERNOR", "years", "Years", 30, "ge"),
    ScenarioSpec("disaster_relief", "DISASTER RELIEF COMMANDER", "days", "Days", 90, "dr"),
    ScenarioSpec("colony_ship", "COLONY SHIP RESOURCE ALLOCATION", "years", "Years", 30, "cs"),
    ScenarioSpec("post_apocalyptic", "POST-APOCALYPTIC REBUILDER", "years", "Years", 30, "pa"),
    ScenarioSpec("film_studio", "FILM STUDIO GREEN-LIGHT", "years", "Years", 30, "fs"),
    ScenarioSpec("accessible_architecture", "ACCESSIBLE ARCHITECTURE FIRM", "years", "Years", 30, "aa"),
    ScenarioSpec("territory_control", "TERRITORY CONTROL", "rounds", "Rounds", 100, "tc"),
    ScenarioSpec("trade_negotiation", "TRADE NEGOTIATION MARATHON", "rounds", "Rounds", 100, "tn"),
    ScenarioSpec("un_crisis", "UN CRISIS RESPONSE", "days", "Days", 90, "uc"),
    ScenarioSpec("civilization_planner", "CIVILIZATION RESOURCE PLANNER", "years", "Years", 30, "cp"),
)

SCENARIO_BY_ID = {spec.simulation_id: spec for spec in SCENARIOS}
SCENARIO_IDS = tuple(spec.simulation_id for spec in SCENARIOS)
PROMPT_CODE_TO_SCENARIO = {
    spec.prompt_code: spec.simulation_id
    for spec in SCENARIOS
    if spec.prompt_code
}


def scenario_ids() -> list[str]:
    """Return supported simulation IDs in display order."""
    return list(SCENARIO_IDS)


def get_scenario(simulation_id: str) -> ScenarioSpec:
    """Return a scenario metadata record by simulation ID."""
    return SCENARIO_BY_ID[simulation_id]


def scenario_label(simulation_id: str) -> str:
    """Return human-facing race title for a simulation ID."""
    return get_scenario(simulation_id).display_name


def scenario_duration_for_args(simulation_id: str, args) -> tuple[str, int]:
    """Return (label, value) duration pair for a parsed argparse namespace."""
    spec = get_scenario(simulation_id)
    return spec.duration_label, getattr(args, spec.duration_arg)
