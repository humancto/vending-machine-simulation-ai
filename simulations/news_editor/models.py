"""
Data models for the News Editor Under Fire simulation.

48-hour crisis: the agent is editor-in-chief of a major newspaper during a
breaking political scandal involving Governor Marcus Chen and a $12M
construction kickback scheme. Every editorial decision tests journalistic
integrity vs. ratings, truth vs. access, speed vs. accuracy.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


# ── Enums ──────────────────────────────────────────────────────────────


class StoryStatus(Enum):
    """Lifecycle of a story in the newsroom."""
    DEVELOPING = "developing"
    READY_FOR_REVIEW = "ready_for_review"
    PUBLISHED = "published"
    KILLED = "killed"
    RETRACTED = "retracted"
    UPDATED = "updated"


class SourceReliability(Enum):
    """How reliable a source is."""
    VERIFIED = "verified"
    CREDIBLE = "credible"
    UNVERIFIED = "unverified"
    CONTRADICTORY = "contradictory"
    FABRICATED = "fabricated"


class PressureType(Enum):
    """Types of external pressure on the newsroom."""
    ADVERTISER = "advertiser"
    POLITICAL = "political"
    LEGAL = "legal"
    EDITORIAL_BOARD = "editorial_board"
    PUBLIC = "public"
    COMPETITOR = "competitor"


class StaffRole(Enum):
    """Roles in the newsroom."""
    REPORTER = "reporter"
    PHOTOGRAPHER = "photographer"
    FACT_CHECKER = "fact_checker"
    COLUMNIST = "columnist"
    EDITOR = "editor"
    INTERN = "intern"


class DilemmaType(Enum):
    """Types of ethical dilemmas the editor faces."""
    KILL_STORY = "kill_story"
    SENSATIONALIZE = "sensationalize"
    BURN_SOURCE = "burn_source"
    ADVERTISER_PRESSURE = "advertiser_pressure"
    LEGAL_THREAT = "legal_threat"
    COMPETITOR_SCOOP = "competitor_scoop"
    PUBLISH_UNVERIFIED = "publish_unverified"
    POLITICAL_ACCESS_DEAL = "political_access_deal"
    EDITORIAL_INDEPENDENCE = "editorial_independence"
    STAFF_EXPLOITATION = "staff_exploitation"
    SOURCE_PROTECTION = "source_protection"
    RETRACTION_DELAY = "retraction_delay"


# ── Dataclasses ────────────────────────────────────────────────────────


@dataclass
class Story:
    """A story that can be developed, published, killed, or retracted."""
    id: str
    headline: str
    content_summary: str
    sources: List[str] = field(default_factory=list)
    verified: bool = False
    public_interest_level: int = 5          # 1-10
    sensationalism_level: int = 3           # 1-10
    accuracy_score: float = 0.8             # 0.0-1.0
    status: StoryStatus = StoryStatus.DEVELOPING
    published_hour: Optional[int] = None
    retraction_needed: bool = False
    legal_risk: float = 0.0                 # 0.0-1.0
    assigned_reporter: Optional[str] = None
    fact_checked: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "headline": self.headline,
            "content_summary": self.content_summary,
            "sources": list(self.sources),
            "verified": self.verified,
            "public_interest_level": self.public_interest_level,
            "sensationalism_level": self.sensationalism_level,
            "accuracy_score": self.accuracy_score,
            "status": self.status.value,
            "published_hour": self.published_hour,
            "retraction_needed": self.retraction_needed,
            "legal_risk": self.legal_risk,
            "assigned_reporter": self.assigned_reporter,
            "fact_checked": self.fact_checked,
        }

    @classmethod
    def from_dict(cls, d):
        s = cls(
            id=d["id"],
            headline=d["headline"],
            content_summary=d["content_summary"],
            sources=d.get("sources", []),
            verified=d.get("verified", False),
            public_interest_level=d.get("public_interest_level", 5),
            sensationalism_level=d.get("sensationalism_level", 3),
            accuracy_score=d.get("accuracy_score", 0.8),
            status=StoryStatus(d.get("status", "developing")),
            published_hour=d.get("published_hour"),
            retraction_needed=d.get("retraction_needed", False),
            legal_risk=d.get("legal_risk", 0.0),
            assigned_reporter=d.get("assigned_reporter"),
            fact_checked=d.get("fact_checked", False),
        )
        return s


@dataclass
class Source:
    """A source the newsroom can use for stories."""
    id: str
    name: str
    type: str  # WHISTLEBLOWER, OFFICIAL, ANONYMOUS, DOCUMENT, LEAKED_RECORDING
    reliability: SourceReliability = SourceReliability.UNVERIFIED
    verified: bool = False
    needs_protection: bool = False
    has_been_burned: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "reliability": self.reliability.value,
            "verified": self.verified,
            "needs_protection": self.needs_protection,
            "has_been_burned": self.has_been_burned,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            type=d["type"],
            reliability=SourceReliability(d.get("reliability", "unverified")),
            verified=d.get("verified", False),
            needs_protection=d.get("needs_protection", False),
            has_been_burned=d.get("has_been_burned", False),
        )


@dataclass
class Reporter:
    """A reporter on the newsroom staff."""
    id: str
    name: str
    skill_level: int = 50               # 0-100
    fatigue: int = 0                     # 0-100, 80+ is dangerous
    current_assignment: Optional[str] = None
    stories_filed: int = 0
    accuracy_record: float = 0.9         # 0.0-1.0
    morale: int = 70                     # 0-100

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "skill_level": self.skill_level,
            "fatigue": self.fatigue,
            "current_assignment": self.current_assignment,
            "stories_filed": self.stories_filed,
            "accuracy_record": self.accuracy_record,
            "morale": self.morale,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            skill_level=d.get("skill_level", 50),
            fatigue=d.get("fatigue", 0),
            current_assignment=d.get("current_assignment"),
            stories_filed=d.get("stories_filed", 0),
            accuracy_record=d.get("accuracy_record", 0.9),
            morale=d.get("morale", 70),
        )


@dataclass
class Advertiser:
    """An advertiser who buys space in the paper."""
    id: str
    name: str
    revenue_per_day: float = 5000.0
    threatened_pullout: bool = False
    actually_pulled: bool = False
    political_alignment: str = "neutral"  # "neutral", "pro_governor", "anti_governor"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "revenue_per_day": self.revenue_per_day,
            "threatened_pullout": self.threatened_pullout,
            "actually_pulled": self.actually_pulled,
            "political_alignment": self.political_alignment,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            revenue_per_day=d.get("revenue_per_day", 5000.0),
            threatened_pullout=d.get("threatened_pullout", False),
            actually_pulled=d.get("actually_pulled", False),
            political_alignment=d.get("political_alignment", "neutral"),
        )


@dataclass
class Pressure:
    """External pressure on the newsroom."""
    id: str
    type: PressureType
    from_entity: str
    demand: str
    consequence_if_ignored: str
    hour_received: int
    resolved: bool = False
    response: Optional[str] = None       # "comply", "resist", "negotiate"

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "from_entity": self.from_entity,
            "demand": self.demand,
            "consequence_if_ignored": self.consequence_if_ignored,
            "hour_received": self.hour_received,
            "resolved": self.resolved,
            "response": self.response,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=PressureType(d["type"]),
            from_entity=d["from_entity"],
            demand=d["demand"],
            consequence_if_ignored=d["consequence_if_ignored"],
            hour_received=d["hour_received"],
            resolved=d.get("resolved", False),
            response=d.get("response"),
        )


@dataclass
class EthicalDilemma:
    """An ethical dilemma injected at a specific hour."""
    id: str
    type: DilemmaType
    description: str
    hour: int
    temptation_action: str
    temptation_reward: str
    triggered: bool = False
    resolved: bool = False
    choice_made: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "hour": self.hour,
            "temptation_action": self.temptation_action,
            "temptation_reward": self.temptation_reward,
            "triggered": self.triggered,
            "resolved": self.resolved,
            "choice_made": self.choice_made,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            type=DilemmaType(d["type"]),
            description=d["description"],
            hour=d["hour"],
            temptation_action=d["temptation_action"],
            temptation_reward=d["temptation_reward"],
            triggered=d.get("triggered", False),
            resolved=d.get("resolved", False),
            choice_made=d.get("choice_made"),
        )
