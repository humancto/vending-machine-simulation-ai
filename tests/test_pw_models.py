"""Tests for simulations/pandemic_ward/models.py -- data models and enums."""

import pytest
from simulations.pandemic_ward.models import (
    DilemmaType,
    EthicalDilemma,
    MediaInquiry,
    Patient,
    PatientCategory,
    PatientStatus,
    PathogenPhase,
    Severity,
    StaffMember,
    StaffRole,
    WardResources,
)


class TestPatientStatusEnum:

    def test_waiting(self):
        assert PatientStatus.WAITING.value == "waiting"

    def test_admitted(self):
        assert PatientStatus.ADMITTED.value == "admitted"

    def test_in_treatment(self):
        assert PatientStatus.IN_TREATMENT.value == "in_treatment"

    def test_on_ventilator(self):
        assert PatientStatus.ON_VENTILATOR.value == "on_ventilator"

    def test_recovering(self):
        assert PatientStatus.RECOVERING.value == "recovering"

    def test_discharged(self):
        assert PatientStatus.DISCHARGED.value == "discharged"

    def test_deceased(self):
        assert PatientStatus.DECEASED.value == "deceased"

    def test_quarantined(self):
        assert PatientStatus.QUARANTINED.value == "quarantined"

    def test_exactly_8_values(self):
        assert len(PatientStatus) == 8


class TestSeverityEnum:

    def test_mild(self):
        assert Severity.MILD.value == "mild"

    def test_moderate(self):
        assert Severity.MODERATE.value == "moderate"

    def test_severe(self):
        assert Severity.SEVERE.value == "severe"

    def test_critical(self):
        assert Severity.CRITICAL.value == "critical"

    def test_exactly_4_values(self):
        assert len(Severity) == 4


class TestPatientCategoryEnum:

    def test_homeless(self):
        assert PatientCategory.HOMELESS.value == "homeless"

    def test_vip_senator(self):
        assert PatientCategory.VIP_SENATOR.value == "vip_senator"

    def test_vip_celebrity(self):
        assert PatientCategory.VIP_CELEBRITY.value == "vip_celebrity"

    def test_uninsured(self):
        assert PatientCategory.UNINSURED.value == "uninsured"

    def test_exactly_7_values(self):
        assert len(PatientCategory) == 7


class TestStaffRoleEnum:

    def test_doctor(self):
        assert StaffRole.DOCTOR.value == "doctor"

    def test_nurse(self):
        assert StaffRole.NURSE.value == "nurse"

    def test_exactly_2_values(self):
        assert len(StaffRole) == 2


class TestPathogenPhaseEnum:

    def test_unknown(self):
        assert PathogenPhase.UNKNOWN.value == "unknown"

    def test_airborne(self):
        assert PathogenPhase.AIRBORNE_CONFIRMED.value == "airborne"

    def test_treatment(self):
        assert PathogenPhase.TREATMENT_EMERGING.value == "treatment"

    def test_vaccine(self):
        assert PathogenPhase.VACCINE_AVAILABLE.value == "vaccine"

    def test_exactly_4_values(self):
        assert len(PathogenPhase) == 4


class TestDilemmaTypeEnum:

    def test_vip_triage(self):
        assert DilemmaType.VIP_TRIAGE.value == "vip_triage"

    def test_experimental_treatment(self):
        assert DilemmaType.EXPERIMENTAL_TREATMENT.value == "experimental_treatment"

    def test_exactly_12_values(self):
        assert len(DilemmaType) == 12


class TestPatientDataclass:

    def _make_patient(self, **overrides):
        defaults = dict(
            id="PW001", name="Test Patient", age=45, gender="M",
            category=PatientCategory.MIDDLE_CLASS,
            severity=Severity.MODERATE,
            original_severity=Severity.MODERATE,
            condition="Fever and cough",
            arrival_day=1,
            needs_ventilator=False,
            has_comorbidities=False,
            consent_given=True,
            family_contactable=True,
            insurance_status="insured",
        )
        defaults.update(overrides)
        return Patient(**defaults)

    def test_default_status_is_waiting(self):
        p = self._make_patient()
        assert p.status == PatientStatus.WAITING

    def test_default_assigned_bed_none(self):
        p = self._make_patient()
        assert p.assigned_bed is None

    def test_default_not_on_experimental(self):
        p = self._make_patient()
        assert p.on_experimental_treatment is False

    def test_default_recovery_zero(self):
        p = self._make_patient()
        assert p.recovery_progress == 0.0

    def test_default_days_waiting_zero(self):
        p = self._make_patient()
        assert p.days_waiting == 0

    def test_default_cause_of_death_none(self):
        p = self._make_patient()
        assert p.cause_of_death is None

    def test_default_family_anxiety_zero(self):
        p = self._make_patient()
        assert p.family_anxiety == 0.0

    def test_all_fields_set(self):
        p = self._make_patient(
            id="PW999", name="Full Patient", age=70,
            severity=Severity.CRITICAL, needs_ventilator=True,
            has_comorbidities=True,
        )
        assert p.id == "PW999"
        assert p.needs_ventilator is True
        assert p.has_comorbidities is True
        assert p.severity == Severity.CRITICAL


class TestStaffMemberDataclass:

    def test_fatigue_starts_at_zero(self):
        s = StaffMember(id="D01", name="Dr. Test", role=StaffRole.DOCTOR)
        assert s.fatigue == 0.0

    def test_on_duty_default_true(self):
        s = StaffMember(id="D01", name="Dr. Test", role=StaffRole.DOCTOR)
        assert s.on_duty is True

    def test_not_infected_default(self):
        s = StaffMember(id="D01", name="Dr. Test", role=StaffRole.DOCTOR)
        assert s.is_infected is False

    def test_not_quarantined_default(self):
        s = StaffMember(id="N01", name="Nurse Test", role=StaffRole.NURSE)
        assert s.is_quarantined is False

    def test_mental_health_starts_at_100(self):
        s = StaffMember(id="D01", name="Dr. Test", role=StaffRole.DOCTOR)
        assert s.mental_health_score == 100.0

    def test_not_resting_default(self):
        s = StaffMember(id="D01", name="Dr. Test", role=StaffRole.DOCTOR)
        assert s.is_resting is False

    def test_no_mandatory_overtime_default(self):
        s = StaffMember(id="N01", name="Nurse Test", role=StaffRole.NURSE)
        assert s.mandatory_overtime is False


class TestEthicalDilemmaDataclass:

    def test_default_not_resolved(self):
        d = EthicalDilemma(
            id="ED01", day=5, dilemma_type=DilemmaType.VIP_TRIAGE,
            title="Test", description="Test dilemma",
        )
        assert d.resolved is False

    def test_default_resolution_none(self):
        d = EthicalDilemma(
            id="ED01", day=5, dilemma_type=DilemmaType.VIP_TRIAGE,
            title="Test", description="Test dilemma",
        )
        assert d.resolution is None


class TestMediaInquiryDataclass:

    def test_default_not_responded(self):
        m = MediaInquiry(id="MI01", day=3, question="Q?", topic="t", urgency="high")
        assert m.responded is False

    def test_default_response_none(self):
        m = MediaInquiry(id="MI01", day=3, question="Q?", topic="t", urgency="high")
        assert m.response is None


class TestWardResources:

    def test_default_beds(self):
        r = WardResources()
        assert r.total_beds == 40

    def test_default_ventilators(self):
        r = WardResources()
        assert r.total_ventilators == 15

    def test_available_beds(self):
        r = WardResources()
        assert r.available_beds() == 40

    def test_available_ventilators(self):
        r = WardResources()
        assert r.available_ventilators() == 15

    def test_occupied_beds_reduce_available(self):
        r = WardResources()
        r.occupied_beds = 10
        assert r.available_beds() == 30

    def test_to_dict(self):
        r = WardResources()
        d = r.to_dict()
        assert "total_beds" in d
        assert "available_beds" in d
        assert "total_ventilators" in d
        assert "ppe_supply" in d
