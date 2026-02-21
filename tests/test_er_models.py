"""Tests for simulations/emergency_room/models.py — data models and enums."""

import pytest
from simulations.emergency_room.models import (
    BLOOD_COMPATIBILITY,
    BloodType,
    MediaInquiry,
    OperatingRoom,
    Patient,
    PatientStatus,
    Socioeconomic,
    StaffMember,
    StaffRole,
)


class TestBloodTypeEnum:

    def test_o_neg_exists(self):
        assert BloodType.O_NEG.value == "O-"

    def test_o_pos_exists(self):
        assert BloodType.O_POS.value == "O+"

    def test_a_neg_exists(self):
        assert BloodType.A_NEG.value == "A-"

    def test_a_pos_exists(self):
        assert BloodType.A_POS.value == "A+"

    def test_b_neg_exists(self):
        assert BloodType.B_NEG.value == "B-"

    def test_b_pos_exists(self):
        assert BloodType.B_POS.value == "B+"

    def test_ab_neg_exists(self):
        assert BloodType.AB_NEG.value == "AB-"

    def test_ab_pos_exists(self):
        assert BloodType.AB_POS.value == "AB+"

    def test_exactly_8_blood_types(self):
        assert len(BloodType) == 8


class TestBloodCompatibility:

    def test_o_neg_donates_to_all(self):
        """O- is the universal donor; it should appear in every recipient's list."""
        for recipient, donors in BLOOD_COMPATIBILITY.items():
            assert BloodType.O_NEG in donors, (
                f"O- missing from {recipient.value}'s compatible donors"
            )

    def test_ab_pos_receives_from_all(self):
        """AB+ is the universal recipient; it should list all 8 blood types."""
        ab_pos_donors = BLOOD_COMPATIBILITY[BloodType.AB_POS]
        for bt in BloodType:
            assert bt in ab_pos_donors, f"{bt.value} not in AB+ donor list"

    def test_o_neg_self_only(self):
        assert BLOOD_COMPATIBILITY[BloodType.O_NEG] == [BloodType.O_NEG]

    def test_o_pos_compatible(self):
        expected = {BloodType.O_NEG, BloodType.O_POS}
        assert set(BLOOD_COMPATIBILITY[BloodType.O_POS]) == expected

    def test_a_neg_compatible(self):
        expected = {BloodType.O_NEG, BloodType.A_NEG}
        assert set(BLOOD_COMPATIBILITY[BloodType.A_NEG]) == expected

    def test_a_pos_compatible(self):
        expected = {BloodType.O_NEG, BloodType.O_POS, BloodType.A_NEG, BloodType.A_POS}
        assert set(BLOOD_COMPATIBILITY[BloodType.A_POS]) == expected

    def test_b_neg_compatible(self):
        expected = {BloodType.O_NEG, BloodType.B_NEG}
        assert set(BLOOD_COMPATIBILITY[BloodType.B_NEG]) == expected

    def test_b_pos_compatible(self):
        expected = {BloodType.O_NEG, BloodType.O_POS, BloodType.B_NEG, BloodType.B_POS}
        assert set(BLOOD_COMPATIBILITY[BloodType.B_POS]) == expected

    def test_ab_neg_compatible(self):
        expected = {BloodType.O_NEG, BloodType.A_NEG, BloodType.B_NEG, BloodType.AB_NEG}
        assert set(BLOOD_COMPATIBILITY[BloodType.AB_NEG]) == expected

    def test_all_recipients_present(self):
        assert len(BLOOD_COMPATIBILITY) == 8


class TestSocioeconomicEnum:

    def test_homeless(self):
        assert Socioeconomic.HOMELESS.value == "homeless"

    def test_working_class(self):
        assert Socioeconomic.WORKING_CLASS.value == "working_class"

    def test_middle_class(self):
        assert Socioeconomic.MIDDLE_CLASS.value == "middle_class"

    def test_upper_class(self):
        assert Socioeconomic.UPPER_CLASS.value == "upper_class"

    def test_vip_politician(self):
        assert Socioeconomic.VIP_POLITICIAN.value == "vip_politician"

    def test_vip_celebrity(self):
        assert Socioeconomic.VIP_CELEBRITY.value == "vip_celebrity"

    def test_exactly_6_values(self):
        assert len(Socioeconomic) == 6


class TestPatientStatusEnum:

    def test_waiting(self):
        assert PatientStatus.WAITING.value == "waiting"

    def test_assigned_bed(self):
        assert PatientStatus.ASSIGNED_BED.value == "assigned_bed"

    def test_in_surgery(self):
        assert PatientStatus.IN_SURGERY.value == "in_surgery"

    def test_recovering(self):
        assert PatientStatus.RECOVERING.value == "recovering"

    def test_discharged(self):
        assert PatientStatus.DISCHARGED.value == "discharged"

    def test_deceased(self):
        assert PatientStatus.DECEASED.value == "deceased"

    def test_exactly_6_values(self):
        assert len(PatientStatus) == 6


class TestStaffRoleEnum:

    def test_surgeon(self):
        assert StaffRole.SURGEON.value == "surgeon"

    def test_nurse(self):
        assert StaffRole.NURSE.value == "nurse"

    def test_exactly_2_values(self):
        assert len(StaffRole) == 2


class TestPatientDataclass:

    def _make_patient(self, **overrides):
        defaults = dict(
            id="P001", name="Test Patient", age=30, gender="M",
            socioeconomic=Socioeconomic.MIDDLE_CLASS,
            triage_score=3, original_triage=3,
            condition="broken ribs", blood_type=BloodType.A_POS,
            needs_surgery=False, surgery_duration_hours=0,
            needs_blood=False, blood_units_needed=0,
            has_dnr=False, deterioration_rate=6.0,
            arrival_hour=0, family_present=True,
        )
        defaults.update(overrides)
        return Patient(**defaults)

    def test_default_status_is_waiting(self):
        p = self._make_patient()
        assert p.status == PatientStatus.WAITING

    def test_default_family_anxiety_zero(self):
        p = self._make_patient()
        assert p.family_anxiety == 0.0

    def test_default_hours_waiting_zero(self):
        p = self._make_patient()
        assert p.hours_waiting == 0

    def test_default_care_level_standard(self):
        p = self._make_patient()
        assert p.care_level == "standard"

    def test_default_assigned_bed_none(self):
        p = self._make_patient()
        assert p.assigned_bed is None

    def test_default_assigned_surgeon_none(self):
        p = self._make_patient()
        assert p.assigned_surgeon is None

    def test_default_not_vip_fast_tracked(self):
        p = self._make_patient()
        assert p.is_vip_fast_tracked is False

    def test_all_fields_set(self):
        p = self._make_patient(
            id="P999", name="Full Patient", age=55, gender="F",
            triage_score=1, needs_surgery=True,
            surgery_duration_hours=4, needs_blood=True,
            blood_units_needed=3, has_dnr=True,
        )
        assert p.id == "P999"
        assert p.needs_surgery is True
        assert p.surgery_duration_hours == 4
        assert p.needs_blood is True
        assert p.blood_units_needed == 3
        assert p.has_dnr is True

    def test_cause_of_death_default_none(self):
        p = self._make_patient()
        assert p.cause_of_death is None

    def test_last_family_update_default(self):
        p = self._make_patient()
        assert p.last_family_update_hour == -1


class TestStaffMemberDataclass:

    def test_fatigue_starts_at_zero(self):
        s = StaffMember(id="S01", name="Dr. Test", role=StaffRole.SURGEON)
        assert s.fatigue == 0.0

    def test_on_duty_default_true(self):
        s = StaffMember(id="S01", name="Dr. Test", role=StaffRole.SURGEON)
        assert s.on_duty is True

    def test_no_current_patient(self):
        s = StaffMember(id="S01", name="Dr. Test", role=StaffRole.SURGEON)
        assert s.current_patient is None

    def test_errors_caused_zero(self):
        s = StaffMember(id="N01", name="Nurse Test", role=StaffRole.NURSE)
        assert s.errors_caused == 0

    def test_breaks_taken_zero(self):
        s = StaffMember(id="N01", name="Nurse Test", role=StaffRole.NURSE)
        assert s.breaks_taken == 0

    def test_not_resting_default(self):
        s = StaffMember(id="S01", name="Dr. Test", role=StaffRole.SURGEON)
        assert s.is_resting is False


class TestOperatingRoomDataclass:

    def test_default_not_in_use(self):
        orr = OperatingRoom(id="OR1")
        assert orr.in_use is False

    def test_default_no_patient(self):
        orr = OperatingRoom(id="OR1")
        assert orr.patient_id is None

    def test_default_no_surgeon(self):
        orr = OperatingRoom(id="OR1")
        assert orr.surgeon_id is None

    def test_default_no_end_hour(self):
        orr = OperatingRoom(id="OR1")
        assert orr.surgery_end_hour is None


class TestMediaInquiryDataclass:

    def test_default_not_responded(self):
        m = MediaInquiry(id="M01", hour=3, question="Q?", topic="t", urgency="high")
        assert m.responded is False

    def test_default_response_none(self):
        m = MediaInquiry(id="M01", hour=3, question="Q?", topic="t", urgency="high")
        assert m.response is None

    def test_all_fields_set(self):
        m = MediaInquiry(
            id="M05", hour=10, question="How many?",
            topic="casualties", urgency="low",
            responded=True, response="All is well",
        )
        assert m.id == "M05"
        assert m.hour == 10
        assert m.responded is True
        assert m.response == "All is well"
