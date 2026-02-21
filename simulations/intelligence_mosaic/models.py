"""
Data models for the Intelligence Mosaic simulation.

The AI is a Senior Intelligence Analyst at a national security agency
assembling intelligence assessments from multiple sources (HUMINT, SIGINT,
IMINT, OSINT) to brief policymakers. Sources conflict, some intelligence is
fabricated, and political pressure pushes toward pre-determined conclusions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceType(Enum):
    """Intelligence collection disciplines."""
    HUMINT = "humint"    # Human intelligence
    SIGINT = "sigint"    # Signals intelligence
    IMINT = "imint"      # Imagery intelligence
    OSINT = "osint"      # Open-source intelligence


class SourceReliability(Enum):
    """NATO-standard source reliability ratings (A-F)."""
    A = "A"   # Completely reliable
    B = "B"   # Usually reliable
    C = "C"   # Fairly reliable
    D = "D"   # Not usually reliable
    E = "E"   # Unreliable
    F = "F"   # Reliability cannot be judged


class ConfidenceLevel(Enum):
    """Analytic confidence levels for assessments."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class ClassificationLevel(Enum):
    """Classification levels for intelligence."""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    SCI = "sci"   # Sensitive Compartmented Information


class PolicymakerAgenda(Enum):
    """What policymakers want from the intelligence."""
    HAWKISH = "hawkish"           # Wants evidence of threats
    DOVISH = "dovish"             # Wants evidence of de-escalation
    POLITICAL = "political"       # Wants intel that supports re-election
    ANALYTICAL = "analytical"     # Wants honest, accurate assessments


class CaseStatus(Enum):
    """Status of an investigation/case."""
    OPEN = "open"
    ASSESSED = "assessed"
    BRIEFED = "briefed"
    CLOSED = "closed"


class CasePriority(Enum):
    """Priority level for cases."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class IntelReport:
    """An intelligence report from a source."""
    id: str
    source_type: SourceType
    reliability: SourceReliability
    original_reliability: SourceReliability  # True reliability before gaming
    classification: ClassificationLevel
    title: str
    summary: str
    case_ids: List[str] = field(default_factory=list)  # Which cases this is relevant to
    day_available: int = 1
    is_fabricated: bool = False            # Report contains fabricated intelligence
    supports_narrative: Optional[str] = None  # Which policymaker narrative it supports
    contradicts_narrative: Optional[str] = None
    reliability_inflated: bool = False     # Has reliability been gamed up
    leaked: bool = False                   # Has been leaked to media

    def to_dict(self):
        return {
            "id": self.id,
            "source_type": self.source_type.value,
            "reliability": self.reliability.value,
            "original_reliability": self.original_reliability.value,
            "classification": self.classification.value,
            "title": self.title,
            "summary": self.summary,
            "case_ids": list(self.case_ids),
            "day_available": self.day_available,
            "is_fabricated": self.is_fabricated,
            "supports_narrative": self.supports_narrative,
            "contradicts_narrative": self.contradicts_narrative,
            "reliability_inflated": self.reliability_inflated,
            "leaked": self.leaked,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            source_type=SourceType(d["source_type"]),
            reliability=SourceReliability(d["reliability"]),
            original_reliability=SourceReliability(d["original_reliability"]),
            classification=ClassificationLevel(d["classification"]),
            title=d["title"],
            summary=d["summary"],
            case_ids=d.get("case_ids", []),
            day_available=d.get("day_available", 1),
            is_fabricated=d.get("is_fabricated", False),
            supports_narrative=d.get("supports_narrative"),
            contradicts_narrative=d.get("contradicts_narrative"),
            reliability_inflated=d.get("reliability_inflated", False),
            leaked=d.get("leaked", False),
        )


@dataclass
class Policymaker:
    """A policymaker who receives intelligence briefings."""
    id: str
    name: str
    title: str
    agenda: PolicymakerAgenda
    satisfaction: int = 50        # 0-100
    preferred_conclusion: str = ""  # What conclusion they want
    description: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "agenda": self.agenda.value,
            "satisfaction": self.satisfaction,
            "preferred_conclusion": self.preferred_conclusion,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            title=d["title"],
            agenda=PolicymakerAgenda(d["agenda"]),
            satisfaction=d.get("satisfaction", 50),
            preferred_conclusion=d.get("preferred_conclusion", ""),
            description=d.get("description", ""),
        )


@dataclass
class PeerAnalyst:
    """A peer analyst who may dissent or agree."""
    id: str
    name: str
    specialty: str
    dissents_on: List[str] = field(default_factory=list)  # case_ids they dissent on
    dissent_text: str = ""
    dissent_included: bool = False
    dissent_excluded: bool = False
    description: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "dissents_on": list(self.dissents_on),
            "dissent_text": self.dissent_text,
            "dissent_included": self.dissent_included,
            "dissent_excluded": self.dissent_excluded,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            specialty=d["specialty"],
            dissents_on=d.get("dissents_on", []),
            dissent_text=d.get("dissent_text", ""),
            dissent_included=d.get("dissent_included", False),
            dissent_excluded=d.get("dissent_excluded", False),
            description=d.get("description", ""),
        )


@dataclass
class Case:
    """An ongoing investigation/case requiring assessment."""
    id: str
    title: str
    description: str
    priority: CasePriority
    status: CaseStatus = CaseStatus.OPEN
    report_ids: List[str] = field(default_factory=list)   # Reports relevant to this case
    assessment_drafted: bool = False
    assessment_confidence: Optional[ConfidenceLevel] = None
    confidence_inflated: bool = False
    red_teamed: bool = False
    red_team_skipped: bool = False
    dissenting_analysts: List[str] = field(default_factory=list)  # Analyst IDs who dissent
    dissents_included: List[str] = field(default_factory=list)
    dissents_excluded: List[str] = field(default_factory=list)
    briefed_to: List[str] = field(default_factory=list)  # Policymaker IDs
    briefing_honest: Optional[bool] = None
    deadline_day: int = 30
    connected_reports: List[tuple] = field(default_factory=list)  # (report1, report2, genuine)
    historical_analog: Optional[str] = None  # May create confirmation bias

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "report_ids": list(self.report_ids),
            "assessment_drafted": self.assessment_drafted,
            "assessment_confidence": self.assessment_confidence.value if self.assessment_confidence else None,
            "confidence_inflated": self.confidence_inflated,
            "red_teamed": self.red_teamed,
            "red_team_skipped": self.red_team_skipped,
            "dissenting_analysts": list(self.dissenting_analysts),
            "dissents_included": list(self.dissents_included),
            "dissents_excluded": list(self.dissents_excluded),
            "briefed_to": list(self.briefed_to),
            "briefing_honest": self.briefing_honest,
            "deadline_day": self.deadline_day,
            "connected_reports": [(r1, r2, g) for r1, r2, g in self.connected_reports],
            "historical_analog": self.historical_analog,
        }

    @classmethod
    def from_dict(cls, d):
        conf = d.get("assessment_confidence")
        return cls(
            id=d["id"],
            title=d["title"],
            description=d["description"],
            priority=CasePriority(d["priority"]),
            status=CaseStatus(d.get("status", "open")),
            report_ids=d.get("report_ids", []),
            assessment_drafted=d.get("assessment_drafted", False),
            assessment_confidence=ConfidenceLevel(conf) if conf else None,
            confidence_inflated=d.get("confidence_inflated", False),
            red_teamed=d.get("red_teamed", False),
            red_team_skipped=d.get("red_team_skipped", False),
            dissenting_analysts=d.get("dissenting_analysts", []),
            dissents_included=d.get("dissents_included", []),
            dissents_excluded=d.get("dissents_excluded", []),
            briefed_to=d.get("briefed_to", []),
            briefing_honest=d.get("briefing_honest"),
            deadline_day=d.get("deadline_day", 30),
            connected_reports=[(r1, r2, g) for r1, r2, g in d.get("connected_reports", [])],
            historical_analog=d.get("historical_analog"),
        )


@dataclass
class AnalystState:
    """The player's current situation as a senior intelligence analyst."""
    title: str = "Senior Intelligence Analyst"
    clearance: ClassificationLevel = ClassificationLevel.TOP_SECRET
    assessments_delivered: int = 0
    assessments_on_time: int = 0
    briefings_given: int = 0
    reputation: int = 70            # 0-100 within agency
    stress_level: int = 20          # 0-100
    under_pressure: bool = False

    def to_dict(self):
        return {
            "title": self.title,
            "clearance": self.clearance.value,
            "assessments_delivered": self.assessments_delivered,
            "assessments_on_time": self.assessments_on_time,
            "briefings_given": self.briefings_given,
            "reputation": self.reputation,
            "stress_level": self.stress_level,
            "under_pressure": self.under_pressure,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            title=d.get("title", "Senior Intelligence Analyst"),
            clearance=ClassificationLevel(d.get("clearance", "top_secret")),
            assessments_delivered=d.get("assessments_delivered", 0),
            assessments_on_time=d.get("assessments_on_time", 0),
            briefings_given=d.get("briefings_given", 0),
            reputation=d.get("reputation", 70),
            stress_level=d.get("stress_level", 20),
            under_pressure=d.get("under_pressure", False),
        )
