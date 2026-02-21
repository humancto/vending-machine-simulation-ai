"""Data models for the Emergency Room Commander simulation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BloodType(Enum):
    O_NEG = "O-"
    O_POS = "O+"
    A_NEG = "A-"
    A_POS = "A+"
    B_NEG = "B-"
    B_POS = "B+"
    AB_NEG = "AB-"
    AB_POS = "AB+"


# Blood compatibility: recipient -> list of compatible donor types
BLOOD_COMPATIBILITY = {
    BloodType.O_NEG:  [BloodType.O_NEG],
    BloodType.O_POS:  [BloodType.O_NEG, BloodType.O_POS],
    BloodType.A_NEG:  [BloodType.O_NEG, BloodType.A_NEG],
    BloodType.A_POS:  [BloodType.O_NEG, BloodType.O_POS, BloodType.A_NEG, BloodType.A_POS],
    BloodType.B_NEG:  [BloodType.O_NEG, BloodType.B_NEG],
    BloodType.B_POS:  [BloodType.O_NEG, BloodType.O_POS, BloodType.B_NEG, BloodType.B_POS],
    BloodType.AB_NEG: [BloodType.O_NEG, BloodType.A_NEG, BloodType.B_NEG, BloodType.AB_NEG],
    BloodType.AB_POS: list(BloodType),  # universal recipient
}


class Socioeconomic(Enum):
    HOMELESS = "homeless"
    WORKING_CLASS = "working_class"
    MIDDLE_CLASS = "middle_class"
    UPPER_CLASS = "upper_class"
    VIP_POLITICIAN = "vip_politician"
    VIP_CELEBRITY = "vip_celebrity"


class PatientStatus(Enum):
    WAITING = "waiting"
    ASSIGNED_BED = "assigned_bed"
    IN_SURGERY = "in_surgery"
    RECOVERING = "recovering"
    DISCHARGED = "discharged"
    DECEASED = "deceased"


class StaffRole(Enum):
    SURGEON = "surgeon"
    NURSE = "nurse"


@dataclass
class Patient:
    id: str
    name: str
    age: int
    gender: str
    socioeconomic: Socioeconomic
    triage_score: int               # 1=immediate, 5=minor
    original_triage: int
    condition: str
    blood_type: BloodType
    needs_surgery: bool
    surgery_duration_hours: int
    needs_blood: bool
    blood_units_needed: int
    has_dnr: bool
    deterioration_rate: float       # hours until triage worsens by 1
    arrival_hour: int
    family_present: bool
    family_anxiety: float = 0.0
    last_family_update_hour: int = -1
    status: PatientStatus = PatientStatus.WAITING
    assigned_bed: Optional[int] = None
    assigned_surgeon: Optional[str] = None
    surgery_start_hour: Optional[int] = None
    hours_waiting: int = 0
    hours_in_bed: int = 0
    treatment_started_hour: Optional[int] = None
    discharged_hour: Optional[int] = None
    cause_of_death: Optional[str] = None
    care_level: str = "standard"
    is_vip_fast_tracked: bool = False


@dataclass
class StaffMember:
    id: str
    name: str
    role: StaffRole
    fatigue: float = 0.0
    on_duty: bool = True
    current_patient: Optional[str] = None
    hours_worked_continuous: int = 0
    total_hours_worked: int = 0
    errors_caused: int = 0
    breaks_taken: int = 0
    is_resting: bool = False
    rest_hours_remaining: int = 0


@dataclass
class OperatingRoom:
    id: str
    in_use: bool = False
    patient_id: Optional[str] = None
    surgeon_id: Optional[str] = None
    surgery_end_hour: Optional[int] = None


@dataclass
class MediaInquiry:
    id: str
    hour: int
    question: str
    topic: str
    urgency: str
    responded: bool = False
    response: Optional[str] = None
