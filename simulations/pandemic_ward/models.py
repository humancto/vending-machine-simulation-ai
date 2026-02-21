"""Data models for the Pandemic Ward Zero simulation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class PatientStatus(Enum):
    WAITING = "waiting"
    ADMITTED = "admitted"
    IN_TREATMENT = "in_treatment"
    ON_VENTILATOR = "on_ventilator"
    RECOVERING = "recovering"
    DISCHARGED = "discharged"
    DECEASED = "deceased"
    QUARANTINED = "quarantined"


class Severity(Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class PatientCategory(Enum):
    HOMELESS = "homeless"
    UNINSURED = "uninsured"
    WORKING_CLASS = "working_class"
    MIDDLE_CLASS = "middle_class"
    UPPER_CLASS = "upper_class"
    VIP_SENATOR = "vip_senator"
    VIP_CELEBRITY = "vip_celebrity"


class StaffRole(Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"


class PathogenPhase(Enum):
    UNKNOWN = "unknown"                    # Day 0-14
    AIRBORNE_CONFIRMED = "airborne"        # Day 15-29
    TREATMENT_EMERGING = "treatment"       # Day 30-49
    VACCINE_AVAILABLE = "vaccine"          # Day 50+


class DilemmaType(Enum):
    VIP_TRIAGE = "vip_triage"
    EXPERIMENTAL_TREATMENT = "experimental_treatment"
    MEDIA_EXPOSE = "media_expose"
    STAFF_REVOLT = "staff_revolt"
    VACCINE_TRIAL = "vaccine_trial"
    QUARANTINE_DECISION = "quarantine_decision"
    PPE_ALLOCATION = "ppe_allocation"
    PHARMA_DEAL = "pharma_deal"
    DISCHARGE_PRESSURE = "discharge_pressure"
    TRIAGE_DISCRIMINATION = "triage_discrimination"
    STAFF_INFECTION = "staff_infection"
    PUBLIC_COMMUNICATION = "public_communication"


@dataclass
class Patient:
    id: str
    name: str
    age: int
    gender: str
    category: PatientCategory
    severity: Severity
    original_severity: Severity
    condition: str
    arrival_day: int
    needs_ventilator: bool
    has_comorbidities: bool
    consent_given: bool                    # Whether patient consented to treatment
    family_contactable: bool
    insurance_status: str                  # "insured", "uninsured", "premium"

    # Mutable state
    status: PatientStatus = PatientStatus.WAITING
    assigned_bed: Optional[int] = None
    on_experimental_treatment: bool = False
    experimental_consent: bool = False
    days_in_ward: int = 0
    days_waiting: int = 0
    recovery_progress: float = 0.0        # 0-100
    infection_confirmed: bool = False
    quarantined: bool = False
    discharged_day: Optional[int] = None
    cause_of_death: Optional[str] = None
    treatment_notes: str = ""
    last_family_update_day: int = -1
    family_anxiety: float = 0.0


@dataclass
class StaffMember:
    id: str
    name: str
    role: StaffRole
    fatigue: float = 0.0                  # 0-100
    exposure_count: int = 0               # Times exposed without PPE
    is_infected: bool = False
    infection_day: Optional[int] = None
    is_quarantined: bool = False
    quarantine_days_left: int = 0
    on_duty: bool = True
    hours_worked_continuous: int = 0
    total_shifts: int = 0
    is_resting: bool = False
    rest_days_remaining: int = 0
    mental_health_score: float = 100.0    # 0-100
    mandatory_overtime: bool = False


@dataclass
class EthicalDilemma:
    id: str
    day: int
    dilemma_type: DilemmaType
    title: str
    description: str
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class MediaInquiry:
    id: str
    day: int
    question: str
    topic: str
    urgency: str
    responded: bool = False
    response: Optional[str] = None


@dataclass
class WardResources:
    total_beds: int = 40
    total_ventilators: int = 15
    ppe_supply: int = 200                 # Units of PPE
    ppe_restock_day: int = 7              # Restocked every 7 days
    ppe_restock_amount: int = 100
    experimental_drug_doses: int = 0
    vaccine_doses: int = 0
    occupied_beds: int = 0
    ventilators_in_use: int = 0

    def available_beds(self):
        return self.total_beds - self.occupied_beds

    def available_ventilators(self):
        return self.total_ventilators - self.ventilators_in_use

    def to_dict(self):
        return {
            "total_beds": self.total_beds,
            "available_beds": self.available_beds(),
            "total_ventilators": self.total_ventilators,
            "available_ventilators": self.available_ventilators(),
            "ppe_supply": self.ppe_supply,
            "experimental_drug_doses": self.experimental_drug_doses,
            "vaccine_doses": self.vaccine_doses,
        }
