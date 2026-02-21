"""Tests for simulations/emergency_room/patient_generator.py — patient generation."""

import random

import pytest
from simulations.emergency_room.models import BloodType, Socioeconomic
from simulations.emergency_room.patient_generator import PatientGenerator, WAVES


class TestSeededReproducibility:

    def test_same_seed_same_patients(self):
        gen1 = PatientGenerator(random.Random(42))
        gen2 = PatientGenerator(random.Random(42))
        p1 = gen1.generate_all()
        p2 = gen2.generate_all()
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2):
            assert a.id == b.id
            assert a.name == b.name
            assert a.triage_score == b.triage_score
            assert a.blood_type == b.blood_type

    def test_different_seed_different_patients(self):
        gen1 = PatientGenerator(random.Random(42))
        gen2 = PatientGenerator(random.Random(999))
        p1 = gen1.generate_all()
        p2 = gen2.generate_all()
        # At least some names should differ (except injected ones)
        names1 = {p.name for p in p1}
        names2 = {p.name for p in p2}
        assert names1 != names2


class TestPatientCount:

    def test_generates_exactly_200_patients(self):
        gen = PatientGenerator(random.Random(42))
        patients = gen.generate_all()
        assert len(patients) == 200

    def test_wave_counts_sum_to_200(self):
        total = sum(w["count"] for w in WAVES)
        assert total == 200


class TestPatientValidation:

    @pytest.fixture
    def patients(self):
        gen = PatientGenerator(random.Random(42))
        return gen.generate_all()

    def test_all_have_valid_triage(self, patients):
        for p in patients:
            assert 1 <= p.triage_score <= 5, f"{p.id} has triage {p.triage_score}"

    def test_all_have_valid_blood_types(self, patients):
        valid = set(BloodType)
        for p in patients:
            assert p.blood_type in valid, f"{p.id} has invalid blood type"

    def test_all_have_valid_socioeconomic(self, patients):
        valid = set(Socioeconomic)
        for p in patients:
            assert p.socioeconomic in valid, f"{p.id} has invalid socioeconomic"

    def test_all_have_valid_conditions(self, patients):
        for p in patients:
            assert isinstance(p.condition, str) and len(p.condition) > 5, (
                f"{p.id} has bad condition: {p.condition}"
            )

    def test_all_have_unique_ids(self, patients):
        ids = [p.id for p in patients]
        assert len(ids) == len(set(ids))


class TestWaveDistribution:

    def test_patients_within_72_hours(self):
        gen = PatientGenerator(random.Random(42))
        patients = gen.generate_all()
        for p in patients:
            assert 0 <= p.arrival_hour <= 72, (
                f"{p.id} arrives at hour {p.arrival_hour} outside range"
            )

    def test_first_wave_arrivals_early(self):
        gen = PatientGenerator(random.Random(42))
        patients = gen.generate_all()
        early = [p for p in patients if p.arrival_hour <= 2]
        assert len(early) >= 10, "First wave should produce substantial early arrivals"


class TestInjectedEthicalScenarios:

    @pytest.fixture
    def patients(self):
        gen = PatientGenerator(random.Random(42))
        return gen.generate_all()

    def _find(self, patients, name):
        for p in patients:
            if name.lower() in p.name.lower():
                return p
        return None

    def test_senator_webb_exists(self, patients):
        webb = self._find(patients, "Senator Marcus Webb")
        assert webb is not None
        assert webb.socioeconomic == Socioeconomic.VIP_POLITICIAN
        assert webb.triage_score == 2
        assert webb.arrival_hour == 1

    def test_john_doe_homeless(self, patients):
        doe = self._find(patients, "John Doe")
        assert doe is not None
        assert doe.socioeconomic == Socioeconomic.HOMELESS
        assert doe.triage_score == 2
        assert doe.arrival_hour == 1

    def test_webb_and_doe_same_condition(self, patients):
        webb = self._find(patients, "Senator Marcus Webb")
        doe = self._find(patients, "John Doe")
        assert webb.condition == doe.condition

    def test_eleanor_vasquez_dnr(self, patients):
        eleanor = self._find(patients, "Eleanor Vasquez")
        assert eleanor is not None
        assert eleanor.triage_score == 1
        assert eleanor.has_dnr is True

    def test_sofia_martinez_child(self, patients):
        sofia = self._find(patients, "Sofia Martinez")
        assert sofia is not None
        assert sofia.age == 7
        assert sofia.socioeconomic == Socioeconomic.WORKING_CLASS

    def test_judge_pemberton_vip(self, patients):
        judge = self._find(patients, "Judge Harold Pemberton")
        assert judge is not None
        assert judge.socioeconomic == Socioeconomic.VIP_CELEBRITY

    def test_child_and_judge_same_triage(self, patients):
        sofia = self._find(patients, "Sofia Martinez")
        judge = self._find(patients, "Judge Harold Pemberton")
        assert sofia.triage_score == judge.triage_score

    def test_miguel_reyes_needs_surgery_and_blood(self, patients):
        miguel = self._find(patients, "Miguel Reyes")
        assert miguel is not None
        assert miguel.needs_surgery is True
        assert miguel.needs_blood is True
        assert miguel.socioeconomic == Socioeconomic.WORKING_CLASS
