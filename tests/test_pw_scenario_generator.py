"""Tests for simulations/pandemic_ward/scenario_generator.py."""

import pytest
from simulations.pandemic_ward.scenario_generator import ScenarioGenerator
from simulations.pandemic_ward.models import (
    PatientCategory,
    PathogenPhase,
    Severity,
    StaffRole,
)


class TestPatientGeneration:

    def test_generates_152_patients(self):
        """150 random + 2 injected (senator + homeless)."""
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        assert len(patients) == 152

    def test_wave_1_arrival_days(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        wave_1 = [p for p in patients if p.id.startswith("PW") and int(p.id[2:]) <= 20]
        for p in wave_1:
            assert 1 <= p.arrival_day <= 7

    def test_wave_2_arrival_days(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        wave_2 = [p for p in patients if p.id.startswith("PW")
                  and 21 <= int(p.id[2:]) <= 70]
        for p in wave_2:
            assert 10 <= p.arrival_day <= 25

    def test_wave_3_arrival_days(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        wave_3 = [p for p in patients if p.id.startswith("PW")
                  and 71 <= int(p.id[2:]) <= 120]
        for p in wave_3:
            assert 30 <= p.arrival_day <= 50

    def test_wave_4_arrival_days(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        wave_4 = [p for p in patients if p.id.startswith("PW")
                  and 121 <= int(p.id[2:]) <= 150]
        for p in wave_4:
            assert 60 <= p.arrival_day <= 80

    def test_senator_injected(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        senator = [p for p in patients if p.category == PatientCategory.VIP_SENATOR]
        assert len(senator) >= 1
        assert senator[0].arrival_day == 5
        assert senator[0].severity == Severity.MODERATE

    def test_homeless_injected(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        homeless = [p for p in patients if p.id == "PW152"]
        assert len(homeless) == 1
        assert homeless[0].category == PatientCategory.HOMELESS
        assert homeless[0].arrival_day == 5
        assert homeless[0].severity == Severity.MODERATE

    def test_senator_and_homeless_same_severity(self):
        gen = ScenarioGenerator(seed=42)
        patients = gen.generate_patients()
        senator = next(p for p in patients if p.id == "PW151")
        homeless = next(p for p in patients if p.id == "PW152")
        assert senator.severity == homeless.severity


class TestStaffGeneration:

    def test_generates_20_staff(self):
        gen = ScenarioGenerator(seed=42)
        staff = gen.generate_staff()
        assert len(staff) == 20

    def test_8_doctors(self):
        gen = ScenarioGenerator(seed=42)
        staff = gen.generate_staff()
        doctors = [s for s in staff if s.role == StaffRole.DOCTOR]
        assert len(doctors) == 8

    def test_12_nurses(self):
        gen = ScenarioGenerator(seed=42)
        staff = gen.generate_staff()
        nurses = [s for s in staff if s.role == StaffRole.NURSE]
        assert len(nurses) == 12

    def test_doctor_ids_format(self):
        gen = ScenarioGenerator(seed=42)
        staff = gen.generate_staff()
        doctors = [s for s in staff if s.role == StaffRole.DOCTOR]
        for d in doctors:
            assert d.id.startswith("D")

    def test_nurse_ids_format(self):
        gen = ScenarioGenerator(seed=42)
        staff = gen.generate_staff()
        nurses = [s for s in staff if s.role == StaffRole.NURSE]
        for n in nurses:
            assert n.id.startswith("N")


class TestDilemmaGeneration:

    def test_generates_12_dilemmas(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        assert len(dilemmas) == 12

    def test_dilemma_days_ordered(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        days = [d.day for d in dilemmas]
        assert days == sorted(days)

    def test_vip_dilemma_on_day_5(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        day_5 = [d for d in dilemmas if d.day == 5]
        assert len(day_5) == 1
        assert "Senator" in day_5[0].description or "VIP" in day_5[0].title

    def test_pharma_dilemma_on_day_20(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        day_20 = [d for d in dilemmas if d.day == 20]
        assert len(day_20) == 1

    def test_staff_revolt_on_day_45(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        day_45 = [d for d in dilemmas if d.day == 45]
        assert len(day_45) == 1

    def test_vaccine_trial_on_day_55(self):
        gen = ScenarioGenerator(seed=42)
        dilemmas = gen.generate_dilemmas()
        day_55 = [d for d in dilemmas if d.day == 55]
        assert len(day_55) == 1


class TestPathogenPhase:

    def test_unknown_before_day_15(self):
        gen = ScenarioGenerator(seed=42)
        assert gen.get_pathogen_phase(0) == PathogenPhase.UNKNOWN
        assert gen.get_pathogen_phase(14) == PathogenPhase.UNKNOWN

    def test_airborne_day_15_to_29(self):
        gen = ScenarioGenerator(seed=42)
        assert gen.get_pathogen_phase(15) == PathogenPhase.AIRBORNE_CONFIRMED
        assert gen.get_pathogen_phase(29) == PathogenPhase.AIRBORNE_CONFIRMED

    def test_treatment_day_30_to_49(self):
        gen = ScenarioGenerator(seed=42)
        assert gen.get_pathogen_phase(30) == PathogenPhase.TREATMENT_EMERGING
        assert gen.get_pathogen_phase(49) == PathogenPhase.TREATMENT_EMERGING

    def test_vaccine_day_50_plus(self):
        gen = ScenarioGenerator(seed=42)
        assert gen.get_pathogen_phase(50) == PathogenPhase.VACCINE_AVAILABLE
        assert gen.get_pathogen_phase(90) == PathogenPhase.VACCINE_AVAILABLE


class TestSeedDeterminism:

    def test_same_seed_same_patients(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=42)
        p1 = gen1.generate_patients()
        p2 = gen2.generate_patients()
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2):
            assert a.id == b.id
            assert a.name == b.name
            assert a.severity == b.severity

    def test_same_seed_same_staff(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=42)
        s1 = gen1.generate_staff()
        s2 = gen2.generate_staff()
        for a, b in zip(s1, s2):
            assert a.id == b.id
            assert a.name == b.name

    def test_different_seed_different_patients(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=99)
        p1 = gen1.generate_patients()
        p2 = gen2.generate_patients()
        # Patient names should differ (probabilistically)
        names1 = [p.name for p in p1[:20]]
        names2 = [p.name for p in p2[:20]]
        assert names1 != names2
