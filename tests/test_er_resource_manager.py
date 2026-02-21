"""Tests for simulations/emergency_room/resource_manager.py — resource management."""

import random

import pytest
from simulations.emergency_room.models import BloodType, BLOOD_COMPATIBILITY
from simulations.emergency_room.resource_manager import (
    INITIAL_BLOOD_SUPPLY,
    ResourceManager,
)


@pytest.fixture
def rm():
    return ResourceManager(random.Random(42))


class TestInitialState:

    def test_total_beds(self, rm):
        assert rm.TOTAL_BEDS == 30

    def test_all_beds_free(self, rm):
        assert len(rm.available_beds()) == 30

    def test_num_surgeons(self, rm):
        assert len(rm.surgeons) == 4

    def test_num_nurses(self, rm):
        assert len(rm.nurses) == 12

    def test_num_ors(self, rm):
        assert len(rm.operating_rooms) == 2

    def test_all_surgeons_available(self, rm):
        assert len(rm.available_surgeons()) == 4

    def test_all_nurses_available(self, rm):
        assert len(rm.available_nurses()) == 12

    def test_all_ors_available(self, rm):
        assert len(rm.available_ors()) == 2

    def test_initial_blood_supply_matches(self, rm):
        for bt, units in INITIAL_BLOOD_SUPPLY.items():
            assert rm.blood_supply[bt] == units


class TestBedManagement:

    def test_assign_bed_success(self, rm):
        assert rm.assign_bed(1, "P001") is True

    def test_assign_bed_occupies(self, rm):
        rm.assign_bed(1, "P001")
        assert rm.beds[1] == "P001"
        assert 1 not in rm.available_beds()

    def test_assign_bed_already_occupied(self, rm):
        rm.assign_bed(1, "P001")
        assert rm.assign_bed(1, "P002") is False

    def test_assign_invalid_bed(self, rm):
        assert rm.assign_bed(999, "P001") is False

    def test_free_bed(self, rm):
        rm.assign_bed(1, "P001")
        pid = rm.free_bed(1)
        assert pid == "P001"
        assert rm.beds[1] is None
        assert 1 in rm.available_beds()

    def test_free_empty_bed(self, rm):
        assert rm.free_bed(1) is None

    def test_find_bed_for_patient(self, rm):
        rm.assign_bed(5, "P003")
        assert rm.find_bed_for_patient("P003") == 5

    def test_find_bed_patient_not_found(self, rm):
        assert rm.find_bed_for_patient("P999") is None

    def test_available_beds_count(self, rm):
        rm.assign_bed(1, "P001")
        rm.assign_bed(2, "P002")
        assert len(rm.available_beds()) == 28


class TestStaffManagement:

    def test_get_staff_by_id_surgeon(self, rm):
        s = rm.get_staff_by_id("S01")
        assert s is not None
        assert s.name == "Dr. Chen"

    def test_get_staff_by_id_nurse(self, rm):
        n = rm.get_staff_by_id("N01")
        assert n is not None
        assert n.name == "Nurse Adams"

    def test_get_staff_by_id_unknown(self, rm):
        assert rm.get_staff_by_id("X99") is None

    def test_available_surgeons_excludes_assigned(self, rm):
        s = rm.surgeons[0]
        s.current_patient = "P001"
        assert s not in rm.available_surgeons()

    def test_available_nurses_excludes_resting(self, rm):
        n = rm.nurses[0]
        n.is_resting = True
        assert n not in rm.available_nurses()


class TestFatigue:

    def test_fatigue_increment_first_8_hours(self, rm):
        s = rm.surgeons[0]
        rm.advance_fatigue()
        assert s.fatigue == 2
        assert s.hours_worked_continuous == 1

    def test_fatigue_increment_hours_8_to_12(self, rm):
        s = rm.surgeons[0]
        s.hours_worked_continuous = 8
        s.fatigue = 16  # 8 hours * 2
        rm.advance_fatigue()
        # Hour 9: in 8-12 range, +4
        assert s.fatigue == 20
        assert s.hours_worked_continuous == 9

    def test_fatigue_increment_beyond_12(self, rm):
        s = rm.surgeons[0]
        s.hours_worked_continuous = 12
        s.fatigue = 32  # accumulated
        rm.advance_fatigue()
        # Hour 13: beyond 12, +6
        assert s.fatigue == 38
        assert s.hours_worked_continuous == 13

    def test_fatigue_capped_at_100(self, rm):
        s = rm.surgeons[0]
        s.fatigue = 99
        s.hours_worked_continuous = 1
        rm.advance_fatigue()
        assert s.fatigue == 100

    def test_resting_staff_recover(self, rm):
        s = rm.surgeons[0]
        s.is_resting = True
        s.rest_hours_remaining = 2
        s.fatigue = 50
        rm.advance_fatigue()
        assert s.fatigue == 42  # -8 per hour
        assert s.rest_hours_remaining == 1

    def test_rest_completed_resets_hours(self, rm):
        s = rm.surgeons[0]
        s.is_resting = True
        s.rest_hours_remaining = 1
        s.fatigue = 20
        s.hours_worked_continuous = 10
        rm.advance_fatigue()
        assert s.is_resting is False
        assert s.rest_hours_remaining == 0
        assert s.hours_worked_continuous == 0

    def test_fatigue_recovery_floors_at_zero(self, rm):
        s = rm.surgeons[0]
        s.is_resting = True
        s.rest_hours_remaining = 2
        s.fatigue = 3
        rm.advance_fatigue()
        assert s.fatigue == 0


class TestErrorProbability:

    def test_zero_at_fatigue_40(self, rm):
        assert rm._error_probability(40) == 0.0

    def test_zero_at_fatigue_0(self, rm):
        assert rm._error_probability(0) == 0.0

    def test_zero_at_fatigue_30(self, rm):
        assert rm._error_probability(30) == 0.0

    def test_scales_above_40(self, rm):
        prob = rm._error_probability(70)
        assert prob > 0
        assert prob < 0.30

    def test_max_at_fatigue_100(self, rm):
        prob = rm._error_probability(100)
        assert abs(prob - 0.30) < 0.001

    def test_linear_midpoint(self, rm):
        # At fatigue 70: (70-40)/60 * 0.30 = 0.15
        prob = rm._error_probability(70)
        assert abs(prob - 0.15) < 0.001


class TestSendToRest:

    def test_send_to_rest_success(self, rm):
        assert rm.send_to_rest("S01", hours=4) is True
        s = rm.get_staff_by_id("S01")
        assert s.is_resting is True
        assert s.rest_hours_remaining == 4
        assert s.current_patient is None

    def test_send_to_rest_increments_breaks(self, rm):
        rm.send_to_rest("S01")
        s = rm.get_staff_by_id("S01")
        assert s.breaks_taken == 1

    def test_send_already_resting(self, rm):
        rm.send_to_rest("S01")
        assert rm.send_to_rest("S01") is False

    def test_send_unknown_staff(self, rm):
        assert rm.send_to_rest("X99") is False


class TestORManagement:

    def test_start_surgery(self, rm):
        result = rm.start_surgery("OR1", "P001", "S01", current_hour=0, duration=3)
        assert result is True

    def test_start_surgery_marks_in_use(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        orr = rm.operating_rooms[0]
        assert orr.in_use is True
        assert orr.patient_id == "P001"
        assert orr.surgeon_id == "S01"
        assert orr.surgery_end_hour == 3

    def test_start_surgery_assigns_surgeon(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        surgeon = rm.get_staff_by_id("S01")
        assert surgeon.current_patient == "P001"

    def test_start_surgery_or_busy(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        assert rm.start_surgery("OR1", "P002", "S02", 0, 2) is False

    def test_check_completed_surgeries(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        completed = rm.check_completed_surgeries(3)
        assert len(completed) == 1
        assert completed[0] == ("OR1", "P001", "S01")

    def test_or_freed_after_completion(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        rm.check_completed_surgeries(3)
        orr = rm.operating_rooms[0]
        assert orr.in_use is False
        assert orr.patient_id is None

    def test_surgeon_freed_after_completion(self, rm):
        rm.start_surgery("OR1", "P001", "S01", 0, 3)
        rm.check_completed_surgeries(3)
        surgeon = rm.get_staff_by_id("S01")
        assert surgeon.current_patient is None


class TestBloodSupply:

    def test_initial_total(self, rm):
        expected = sum(INITIAL_BLOOD_SUPPLY.values())
        assert rm.get_total_blood_units() == expected

    def test_initial_o_neg(self, rm):
        assert rm.blood_supply[BloodType.O_NEG] == 20

    def test_check_blood_compatible_success(self, rm):
        available, types = rm.check_blood_compatible(BloodType.A_POS, 2)
        assert available is True
        assert len(types) > 0

    def test_check_blood_compatible_too_many(self, rm):
        available, _ = rm.check_blood_compatible(BloodType.AB_NEG, 999)
        assert available is False

    def test_use_blood_exact_match_first(self, rm):
        initial_a_pos = rm.blood_supply[BloodType.A_POS]
        success, used = rm.use_blood(BloodType.A_POS, 2)
        assert success is True
        assert BloodType.A_POS in used
        assert rm.blood_supply[BloodType.A_POS] == initial_a_pos - 2

    def test_use_blood_falls_to_compatible(self, rm):
        # Drain exact match first
        rm.blood_supply[BloodType.B_NEG] = 0
        success, used = rm.use_blood(BloodType.B_NEG, 1)
        assert success is True
        # Should have used O- since it's the only other compatible type
        assert BloodType.O_NEG in used

    def test_use_blood_insufficient(self, rm):
        success, used = rm.use_blood(BloodType.O_NEG, 999)
        assert success is False

    def test_blood_compatibility_o_neg_to_all(self, rm):
        """O- blood should be compatible with every blood type."""
        for bt in BloodType:
            compatible_donors = BLOOD_COMPATIBILITY[bt]
            assert BloodType.O_NEG in compatible_donors

    def test_blood_compatibility_ab_pos_from_all(self, rm):
        """AB+ should accept all blood types."""
        donors = BLOOD_COMPATIBILITY[BloodType.AB_POS]
        assert set(donors) == set(BloodType)
