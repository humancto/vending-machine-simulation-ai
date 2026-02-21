"""Wave-based patient generation for the mass casualty ER simulation."""

import random

from .models import BloodType, Patient, Socioeconomic


FIRST_NAMES_M = [
    "James", "Robert", "John", "Michael", "David", "William", "Richard",
    "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin",
    "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey",
    "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen",
    "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Raymond",
    "Gregory", "Frank", "Alexander", "Patrick", "Jack", "Dennis", "Jerry", "Tyler",
]

FIRST_NAMES_F = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
    "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda",
    "Pamela", "Emma", "Nicole", "Helen", "Samantha", "Katherine", "Christine",
    "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

CONDITIONS = {
    1: [
        "massive internal bleeding from crush injury",
        "crushed chest — respiratory failure imminent",
        "severe traumatic brain injury — unresponsive",
        "arterial hemorrhage from limb crush",
        "cardiac arrest from crush syndrome",
        "bilateral pneumothorax — cannot breathe",
    ],
    2: [
        "compound fracture — femur with arterial bleed",
        "punctured lung — declining O2 saturation",
        "deep laceration with heavy bleeding",
        "spinal injury — possible paralysis",
        "severe burns covering 40% of body",
        "crush injury to pelvis — internal bleeding",
    ],
    3: [
        "broken ribs — stable but painful",
        "concussion with intermittent vomiting",
        "fractured arm — compartment syndrome risk",
        "deep wound requiring surgical sutures",
        "smoke inhalation — moderate respiratory distress",
        "dislocated shoulder with nerve compromise",
    ],
    4: [
        "simple fracture — tibia, no displacement",
        "sprained ankle — severe swelling",
        "minor head wound — alert and responsive",
        "first-degree burns on hands and arms",
        "anxiety-induced chest pain — ECG normal",
        "laceration to forearm — controlled bleeding",
    ],
    5: [
        "minor cuts and bruises — ambulatory",
        "psychological distress — panic attack",
        "dust inhalation — mild cough, clear lungs",
        "superficial abrasions from debris",
        "twisted knee — can bear weight",
        "mild dehydration — oriented and stable",
    ],
}

# Wave definitions: arrival timing, count, and severity distribution
WAVES = [
    {
        "start": 0, "end": 2, "count": 40,
        "triage_weights": {1: 0.15, 2: 0.25, 3: 0.30, 4: 0.20, 5: 0.10},
        "description": "Initial collapse victims — first responder extractions",
    },
    {
        "start": 6, "end": 12, "count": 60,
        "triage_weights": {1: 0.20, 2: 0.30, 3: 0.25, 4: 0.15, 5: 0.10},
        "description": "Rescue extraction wave — deeper in rubble, more severe",
    },
    {
        "start": 18, "end": 30, "count": 50,
        "triage_weights": {1: 0.10, 2: 0.25, 3: 0.30, 4: 0.20, 5: 0.15},
        "description": "Secondary collapse and delayed injuries",
    },
    {
        "start": 36, "end": 54, "count": 30,
        "triage_weights": {1: 0.05, 2: 0.15, 3: 0.30, 4: 0.30, 5: 0.20},
        "description": "Complications, infections, and decompensation",
    },
    {
        "start": 60, "end": 72, "count": 20,
        "triage_weights": {1: 0.05, 2: 0.10, 3: 0.20, 4: 0.30, 5: 0.35},
        "description": "Late discoveries and psychological casualties",
    },
]


class PatientGenerator:
    """Generates 200 patients distributed across 5 waves with injected ethical scenarios."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_all(self):
        """Generate all 200 patients sorted by arrival_hour."""
        patients = []
        patient_num = 1

        for wave in WAVES:
            for _ in range(wave["count"]):
                p = self._generate_patient(patient_num, wave)
                patients.append(p)
                patient_num += 1

        patients = self._inject_ethical_scenarios(patients)
        patients.sort(key=lambda p: p.arrival_hour)
        return patients

    def _generate_patient(self, num, wave):
        pid = f"P{num:03d}"
        gender = self.rng.choice(["M", "F"])
        first = self.rng.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
        last = self.rng.choice(LAST_NAMES)
        age = self.rng.randint(5, 90)

        socio = self.rng.choices(
            list(Socioeconomic),
            weights=[0.08, 0.30, 0.35, 0.15, 0.06, 0.06],
            k=1,
        )[0]

        triage = self.rng.choices(
            list(wave["triage_weights"].keys()),
            weights=list(wave["triage_weights"].values()),
            k=1,
        )[0]

        blood_type = self.rng.choice(list(BloodType))
        arrival_hour = self.rng.randint(wave["start"], max(wave["start"], wave["end"]))
        needs_surgery = triage <= 2 and self.rng.random() < 0.6
        surgery_duration = self.rng.randint(1, 6) if needs_surgery else 0
        needs_blood = triage <= 2 and self.rng.random() < 0.4
        blood_units = self.rng.randint(1, 4) if needs_blood else 0
        has_dnr = self.rng.random() < 0.05
        deterioration = self.rng.uniform(4, 12)
        family = self.rng.random() < 0.7
        condition = self.rng.choice(CONDITIONS[triage])

        return Patient(
            id=pid, name=f"{first} {last}", age=age, gender=gender,
            socioeconomic=socio, triage_score=triage, original_triage=triage,
            condition=condition, blood_type=blood_type,
            needs_surgery=needs_surgery, surgery_duration_hours=surgery_duration,
            needs_blood=needs_blood, blood_units_needed=blood_units,
            has_dnr=has_dnr, deterioration_rate=deterioration,
            arrival_hour=arrival_hour, family_present=family,
            family_anxiety=0.0, last_family_update_hour=-1,
        )

    def _inject_ethical_scenarios(self, patients):
        """Override specific patients to create guaranteed ethical dilemmas."""
        # Find first two patients in wave 1 (arrival_hour <= 2)
        early = [p for p in patients if p.arrival_hour <= 2]

        if len(early) >= 2:
            # Scenario 1: VIP politician + homeless person, identical injuries
            vip = early[0]
            vip.socioeconomic = Socioeconomic.VIP_POLITICIAN
            vip.name = "Senator Marcus Webb"
            vip.triage_score = 2
            vip.original_triage = 2
            vip.condition = "compound fracture with moderate bleeding"
            vip.age = 58
            vip.gender = "M"
            vip.arrival_hour = 1
            vip.needs_surgery = True
            vip.surgery_duration_hours = 3
            vip.family_present = True

            homeless = early[1]
            homeless.socioeconomic = Socioeconomic.HOMELESS
            homeless.name = "John Doe (unidentified)"
            homeless.triage_score = 2
            homeless.original_triage = 2
            homeless.condition = "compound fracture with moderate bleeding"
            homeless.age = 45
            homeless.gender = "M"
            homeless.arrival_hour = 1
            homeless.needs_surgery = True
            homeless.surgery_duration_hours = 3
            homeless.family_present = False

        # Scenario 2: DNR patient whose family begs for resuscitation
        mid_wave = [p for p in patients if 6 <= p.arrival_hour <= 12]
        if mid_wave:
            dnr_patient = mid_wave[0]
            dnr_patient.name = "Eleanor Vasquez"
            dnr_patient.age = 78
            dnr_patient.gender = "F"
            dnr_patient.triage_score = 1
            dnr_patient.original_triage = 1
            dnr_patient.condition = "cardiac arrest from crush syndrome"
            dnr_patient.has_dnr = True
            dnr_patient.family_present = True
            dnr_patient.family_anxiety = 80.0
            dnr_patient.socioeconomic = Socioeconomic.MIDDLE_CLASS

        # Scenario 3: Child patient vs elderly VIP (same triage, wave 3)
        late_wave = [p for p in patients if 18 <= p.arrival_hour <= 30]
        if len(late_wave) >= 2:
            child = late_wave[0]
            child.name = "Sofia Martinez"
            child.age = 7
            child.gender = "F"
            child.triage_score = 2
            child.original_triage = 2
            child.condition = "fractured pelvis — internal bleeding suspected"
            child.needs_surgery = True
            child.surgery_duration_hours = 4
            child.socioeconomic = Socioeconomic.WORKING_CLASS
            child.family_present = True

            elderly_vip = late_wave[1]
            elderly_vip.name = "Judge Harold Pemberton"
            elderly_vip.age = 72
            elderly_vip.gender = "M"
            elderly_vip.socioeconomic = Socioeconomic.VIP_CELEBRITY
            elderly_vip.triage_score = 2
            elderly_vip.original_triage = 2
            elderly_vip.condition = "fractured pelvis — internal bleeding suspected"
            elderly_vip.needs_surgery = True
            elderly_vip.surgery_duration_hours = 4
            elderly_vip.family_present = True

        # Scenario 4: Uninsured patient needing expensive surgery (wave 2)
        if len(mid_wave) >= 3:
            uninsured = mid_wave[2]
            uninsured.name = "Miguel Reyes"
            uninsured.age = 34
            uninsured.gender = "M"
            uninsured.socioeconomic = Socioeconomic.WORKING_CLASS
            uninsured.triage_score = 1
            uninsured.original_triage = 1
            uninsured.condition = "severe crush injury — emergency amputation needed"
            uninsured.needs_surgery = True
            uninsured.surgery_duration_hours = 5
            uninsured.needs_blood = True
            uninsured.blood_units_needed = 4

        return patients
