"""Resource management for the Emergency Room Commander simulation.

Tracks beds, surgeons, nurses, operating rooms, and blood supply.
Manages staff fatigue, error probability, and resource allocation.
"""

import random

from .models import (
    BloodType, BLOOD_COMPATIBILITY, OperatingRoom, PatientStatus,
    StaffMember, StaffRole,
)

# Initial blood supply (units)
INITIAL_BLOOD_SUPPLY = {
    BloodType.O_NEG: 20,
    BloodType.O_POS: 30,
    BloodType.A_NEG: 10,
    BloodType.A_POS: 25,
    BloodType.B_NEG: 8,
    BloodType.B_POS: 15,
    BloodType.AB_NEG: 5,
    BloodType.AB_POS: 10,
}

SURGEON_NAMES = ["Dr. Chen", "Dr. Kapoor", "Dr. Okafor", "Dr. Reyes"]
NURSE_NAMES = [
    "Nurse Adams", "Nurse Brooks", "Nurse Cruz", "Nurse Diaz",
    "Nurse Evans", "Nurse Flores", "Nurse Grant", "Nurse Hayes",
    "Nurse Ivers", "Nurse Jones", "Nurse Kim", "Nurse Lopez",
]


class ResourceManager:
    """Manages hospital resources: beds, staff, ORs, and blood supply."""

    TOTAL_BEDS = 30
    NUM_SURGEONS = 4
    NUM_NURSES = 12
    NUM_ORS = 2

    def __init__(self, rng: random.Random):
        self.rng = rng

        # Beds: index -> patient_id or None
        self.beds = {i: None for i in range(1, self.TOTAL_BEDS + 1)}

        # Staff
        self.surgeons = [
            StaffMember(id=f"S{i+1:02d}", name=SURGEON_NAMES[i], role=StaffRole.SURGEON)
            for i in range(self.NUM_SURGEONS)
        ]
        self.nurses = [
            StaffMember(id=f"N{i+1:02d}", name=NURSE_NAMES[i], role=StaffRole.NURSE)
            for i in range(self.NUM_NURSES)
        ]

        # Operating rooms
        self.operating_rooms = [
            OperatingRoom(id=f"OR{i+1}")
            for i in range(self.NUM_ORS)
        ]

        # Blood supply
        self.blood_supply = dict(INITIAL_BLOOD_SUPPLY)

        # Tracking
        self.total_blood_used = 0
        self.total_surgeries = 0
        self.fatigue_errors = 0

    # ── Bed Management ─────────────────────────────────────────────────

    def available_beds(self):
        """Return list of free bed numbers."""
        return [num for num, pid in self.beds.items() if pid is None]

    def occupied_beds(self):
        """Return dict of bed_num -> patient_id for occupied beds."""
        return {num: pid for num, pid in self.beds.items() if pid is not None}

    def assign_bed(self, bed_num, patient_id):
        """Assign a patient to a bed. Returns True on success."""
        if bed_num not in self.beds:
            return False
        if self.beds[bed_num] is not None:
            return False
        self.beds[bed_num] = patient_id
        return True

    def free_bed(self, bed_num):
        """Free a bed. Returns the patient_id that was in it, or None."""
        if bed_num not in self.beds:
            return None
        pid = self.beds[bed_num]
        self.beds[bed_num] = None
        return pid

    def find_bed_for_patient(self, patient_id):
        """Find which bed a patient is in. Returns bed_num or None."""
        for num, pid in self.beds.items():
            if pid == patient_id:
                return num
        return None

    # ── Staff Management ───────────────────────────────────────────────

    def get_all_staff(self):
        """Return all staff members."""
        return self.surgeons + self.nurses

    def get_staff_by_id(self, staff_id):
        """Find a staff member by ID."""
        for s in self.get_all_staff():
            if s.id == staff_id:
                return s
        return None

    def available_surgeons(self):
        """Return surgeons that are on duty and not currently assigned."""
        return [
            s for s in self.surgeons
            if s.on_duty and not s.is_resting and s.current_patient is None
        ]

    def available_nurses(self):
        """Return nurses that are on duty and not currently assigned."""
        return [
            n for n in self.nurses
            if n.on_duty and not n.is_resting and n.current_patient is None
        ]

    def advance_fatigue(self):
        """Advance fatigue for all on-duty staff by 1 hour.

        Fatigue rates:
          - Hours 0-8: +2 per hour
          - Hours 8-12: +4 per hour
          - Hours 12+: +6 per hour

        Returns list of error events (staff_id, patient_id) from fatigue.
        """
        errors = []
        for staff in self.get_all_staff():
            if staff.is_resting:
                staff.rest_hours_remaining -= 1
                staff.fatigue = max(0, staff.fatigue - 8)
                if staff.rest_hours_remaining <= 0:
                    staff.is_resting = False
                    staff.rest_hours_remaining = 0
                    staff.hours_worked_continuous = 0
                continue

            if not staff.on_duty:
                continue

            staff.hours_worked_continuous += 1
            staff.total_hours_worked += 1

            # Fatigue increment based on hours worked
            if staff.hours_worked_continuous <= 8:
                staff.fatigue = min(100, staff.fatigue + 2)
            elif staff.hours_worked_continuous <= 12:
                staff.fatigue = min(100, staff.fatigue + 4)
            else:
                staff.fatigue = min(100, staff.fatigue + 6)

            # Error probability based on fatigue
            error_prob = self._error_probability(staff.fatigue)
            if error_prob > 0 and staff.current_patient and self.rng.random() < error_prob:
                staff.errors_caused += 1
                self.fatigue_errors += 1
                errors.append((staff.id, staff.current_patient))

        return errors

    def _error_probability(self, fatigue):
        """Calculate error probability from fatigue level.

        0% at fatigue <= 40, scales linearly to 30% at fatigue == 100.
        """
        if fatigue <= 40:
            return 0.0
        return min(0.30, (fatigue - 40) / 60 * 0.30)

    def send_to_rest(self, staff_id, hours=4):
        """Send a staff member to rest.

        Returns True on success, False if staff not found or already resting.
        """
        staff = self.get_staff_by_id(staff_id)
        if staff is None:
            return False
        if staff.is_resting:
            return False
        staff.is_resting = True
        staff.rest_hours_remaining = hours
        staff.current_patient = None
        staff.breaks_taken += 1
        return True

    def get_staff_summary(self):
        """Return a summary of all staff status."""
        result = []
        for s in self.get_all_staff():
            result.append({
                "id": s.id,
                "name": s.name,
                "role": s.role.value,
                "fatigue": round(s.fatigue, 1),
                "hours_worked": s.hours_worked_continuous,
                "total_hours": s.total_hours_worked,
                "current_patient": s.current_patient,
                "is_resting": s.is_resting,
                "rest_remaining": s.rest_hours_remaining,
                "errors": s.errors_caused,
                "breaks": s.breaks_taken,
            })
        return result

    # ── Operating Room Management ──────────────────────────────────────

    def available_ors(self):
        """Return list of available operating rooms."""
        return [orr for orr in self.operating_rooms if not orr.in_use]

    def start_surgery(self, or_id, patient_id, surgeon_id, current_hour, duration):
        """Start a surgery in an OR.

        Returns True on success.
        """
        orr = None
        for o in self.operating_rooms:
            if o.id == or_id and not o.in_use:
                orr = o
                break
        if orr is None:
            return False

        surgeon = self.get_staff_by_id(surgeon_id)
        if surgeon is None or surgeon.current_patient is not None:
            return False

        orr.in_use = True
        orr.patient_id = patient_id
        orr.surgeon_id = surgeon_id
        orr.surgery_end_hour = current_hour + duration
        surgeon.current_patient = patient_id
        self.total_surgeries += 1
        return True

    def check_completed_surgeries(self, current_hour):
        """Check for completed surgeries.

        Returns list of (or_id, patient_id, surgeon_id) for completed ones.
        """
        completed = []
        for orr in self.operating_rooms:
            if orr.in_use and orr.surgery_end_hour is not None and current_hour >= orr.surgery_end_hour:
                completed.append((orr.id, orr.patient_id, orr.surgeon_id))
                # Free the OR
                surgeon = self.get_staff_by_id(orr.surgeon_id)
                if surgeon:
                    surgeon.current_patient = None
                orr.in_use = False
                orr.patient_id = None
                orr.surgeon_id = None
                orr.surgery_end_hour = None
        return completed

    # ── Blood Supply ───────────────────────────────────────────────────

    def get_blood_supply(self):
        """Return current blood supply as dict."""
        return {bt.value: units for bt, units in self.blood_supply.items()}

    def check_blood_compatible(self, patient_blood_type, units_needed):
        """Check if compatible blood is available.

        Returns (available: bool, compatible_types: list of (BloodType, available_units)).
        """
        compatible = BLOOD_COMPATIBILITY.get(patient_blood_type, [])
        available = []
        total = 0
        for bt in compatible:
            units = self.blood_supply.get(bt, 0)
            if units > 0:
                available.append((bt, units))
                total += units
        return total >= units_needed, available

    def use_blood(self, patient_blood_type, units_needed):
        """Use blood units for a patient, drawing from compatible types.

        Returns (success: bool, units_used: dict of BloodType -> units).
        """
        compatible = BLOOD_COMPATIBILITY.get(patient_blood_type, [])
        remaining = units_needed
        used = {}

        # Use exact match first, then compatible types
        ordered = [patient_blood_type] + [bt for bt in compatible if bt != patient_blood_type]

        for bt in ordered:
            if remaining <= 0:
                break
            available = self.blood_supply.get(bt, 0)
            if available > 0:
                take = min(available, remaining)
                self.blood_supply[bt] -= take
                used[bt] = take
                remaining -= take
                self.total_blood_used += take

        return remaining == 0, used

    def get_total_blood_units(self):
        """Return total blood units across all types."""
        return sum(self.blood_supply.values())

    # ── Summary ────────────────────────────────────────────────────────

    def get_resource_summary(self):
        """Return a complete resource status."""
        return {
            "beds": {
                "total": self.TOTAL_BEDS,
                "available": len(self.available_beds()),
                "occupied": self.TOTAL_BEDS - len(self.available_beds()),
            },
            "surgeons": {
                "total": self.NUM_SURGEONS,
                "available": len(self.available_surgeons()),
                "avg_fatigue": round(
                    sum(s.fatigue for s in self.surgeons) / max(1, len(self.surgeons)), 1
                ),
            },
            "nurses": {
                "total": self.NUM_NURSES,
                "available": len(self.available_nurses()),
                "avg_fatigue": round(
                    sum(n.fatigue for n in self.nurses) / max(1, len(self.nurses)), 1
                ),
            },
            "operating_rooms": {
                "total": self.NUM_ORS,
                "available": len(self.available_ors()),
            },
            "blood_supply": self.get_blood_supply(),
            "total_blood_units": self.get_total_blood_units(),
            "stats": {
                "total_surgeries": self.total_surgeries,
                "total_blood_used": self.total_blood_used,
                "fatigue_errors": self.fatigue_errors,
            },
        }
