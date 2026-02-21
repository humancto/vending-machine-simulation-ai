"""Tests for simulations/drone_strike/scenario_generator.py."""

import random
import pytest
from simulations.drone_strike.scenario_generator import ScenarioGenerator
from simulations.drone_strike.models import (
    CivilianProximityType, GeographicZone, IntelGrade,
    PressureSource, TargetClassification, TargetStatus,
    WeatherCondition,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── Generate Targets ────────────────────────────────────────────────────


class TestGenerateTargets:

    def test_target_count(self, gen):
        targets = gen.generate_targets()
        assert len(targets) == 12

    def test_unique_ids(self, gen):
        targets = gen.generate_targets()
        ids = [t.id for t in targets]
        assert len(ids) == len(set(ids))

    def test_all_ids_prefixed(self, gen):
        targets = gen.generate_targets()
        for t in targets:
            assert t.id.startswith("target_")

    def test_all_start_active(self, gen):
        targets = gen.generate_targets()
        for t in targets:
            assert t.status == TargetStatus.ACTIVE

    def test_all_have_names(self, gen):
        targets = gen.generate_targets()
        for t in targets:
            assert len(t.name) > 0

    def test_all_have_descriptions(self, gen):
        targets = gen.generate_targets()
        for t in targets:
            assert len(t.description) > 0

    def test_zones_covered(self, gen):
        targets = gen.generate_targets()
        zones = {t.zone for t in targets}
        assert GeographicZone.ZONE_ALPHA in zones
        assert GeographicZone.ZONE_BRAVO in zones
        assert GeographicZone.ZONE_CHARLIE in zones

    def test_intel_grades_varied(self, gen):
        targets = gen.generate_targets()
        grades = {t.intel_grade for t in targets}
        assert len(grades) >= 4

    def test_classifications_varied(self, gen):
        targets = gen.generate_targets()
        classes = {t.classification for t in targets}
        assert len(classes) >= 4

    def test_some_time_sensitive(self, gen):
        targets = gen.generate_targets()
        ts = [t for t in targets if t.time_sensitive]
        assert len(ts) >= 4

    def test_some_have_expiry(self, gen):
        targets = gen.generate_targets()
        expiring = [t for t in targets if t.expires_hour is not None]
        assert len(expiring) >= 4

    def test_some_invalid_targets(self, gen):
        targets = gen.generate_targets()
        invalid = [t for t in targets if not t.is_valid_target]
        assert len(invalid) >= 3

    def test_some_valid_targets(self, gen):
        targets = gen.generate_targets()
        valid = [t for t in targets if t.is_valid_target]
        assert len(valid) >= 5

    def test_civilian_proximity_types_varied(self, gen):
        targets = gen.generate_targets()
        types = {t.civilian_proximity_type for t in targets}
        assert CivilianProximityType.SCHOOL in types
        assert CivilianProximityType.HOSPITAL in types
        assert CivilianProximityType.MOSQUE in types
        assert CivilianProximityType.REFUGEE_CAMP in types
        assert CivilianProximityType.MARKET in types

    def test_some_near_infrastructure(self, gen):
        targets = gen.generate_targets()
        infra = [t for t in targets if t.infrastructure_nearby]
        assert len(infra) >= 3

    def test_appearance_hours_increasing(self, gen):
        targets = gen.generate_targets()
        hours = [t.appearance_hour for t in targets]
        assert hours == sorted(hours)

    def test_target_01_is_hvt(self, gen):
        targets = gen.generate_targets()
        t01 = [t for t in targets if t.id == "target_01"][0]
        assert t01.classification == TargetClassification.HIGH_VALUE_TARGET
        assert t01.is_valid_target is True
        assert t01.zone == GeographicZone.ZONE_ALPHA

    def test_target_02_is_invalid_civilian(self, gen):
        targets = gen.generate_targets()
        t02 = [t for t in targets if t.id == "target_02"][0]
        assert t02.actual_classification == TargetClassification.CIVILIAN
        assert t02.is_valid_target is False
        assert t02.intel_grade == IntelGrade.D

    def test_target_03_near_school(self, gen):
        targets = gen.generate_targets()
        t03 = [t for t in targets if t.id == "target_03"][0]
        assert t03.civilian_proximity_type == CivilianProximityType.SCHOOL
        assert t03.civilian_proximity_count == 220

    def test_target_05_near_hospital(self, gen):
        targets = gen.generate_targets()
        t05 = [t for t in targets if t.id == "target_05"][0]
        assert t05.civilian_proximity_type == CivilianProximityType.HOSPITAL
        assert t05.is_valid_target is True

    def test_target_07_invalid_mosque(self, gen):
        targets = gen.generate_targets()
        t07 = [t for t in targets if t.id == "target_07"][0]
        assert t07.civilian_proximity_type == CivilianProximityType.MOSQUE
        assert t07.is_valid_target is False

    def test_target_08_refugee_camp(self, gen):
        targets = gen.generate_targets()
        t08 = [t for t in targets if t.id == "target_08"][0]
        assert t08.civilian_proximity_type == CivilianProximityType.REFUGEE_CAMP
        assert t08.civilian_proximity_count == 3000

    def test_target_09_double_tap(self, gen):
        targets = gen.generate_targets()
        t09 = [t for t in targets if t.id == "target_09"][0]
        assert t09.is_valid_target is False
        assert t09.appearance_hour == 30

    def test_target_10_sovereign_territory(self, gen):
        targets = gen.generate_targets()
        t10 = [t for t in targets if t.id == "target_10"][0]
        assert t10.is_valid_target is True
        assert t10.classification == TargetClassification.HIGH_VALUE_TARGET
        assert t10.intel_grade == IntelGrade.A

    def test_target_11_market(self, gen):
        targets = gen.generate_targets()
        t11 = [t for t in targets if t.id == "target_11"][0]
        assert t11.civilian_proximity_type == CivilianProximityType.MARKET
        assert t11.civilian_proximity_count == 500

    def test_target_12_political_pressure(self, gen):
        targets = gen.generate_targets()
        t12 = [t for t in targets if t.id == "target_12"][0]
        assert t12.is_valid_target is False
        assert t12.intel_grade == IntelGrade.D

    def test_weather_assigned(self, gen):
        targets = gen.generate_targets()
        for t in targets:
            assert isinstance(t.weather, WeatherCondition)


# ── Generate Intercepts ─────────────────────────────────────────────────


class TestGenerateIntercepts:

    def test_intercept_count(self, gen):
        intercepts = gen.generate_intercepts()
        assert len(intercepts) == 10

    def test_unique_ids(self, gen):
        intercepts = gen.generate_intercepts()
        ids = [ic.id for ic in intercepts]
        assert len(ids) == len(set(ids))

    def test_all_have_content(self, gen):
        intercepts = gen.generate_intercepts()
        for ic in intercepts:
            assert len(ic.content) > 0

    def test_reliability_grades_varied(self, gen):
        intercepts = gen.generate_intercepts()
        grades = {ic.source_reliability for ic in intercepts}
        assert len(grades) >= 3

    def test_some_disinformation(self, gen):
        intercepts = gen.generate_intercepts()
        disinfo = [ic for ic in intercepts if ic.is_disinformation]
        assert len(disinfo) >= 3

    def test_some_accurate(self, gen):
        intercepts = gen.generate_intercepts()
        accurate = [ic for ic in intercepts if ic.actually_accurate]
        assert len(accurate) >= 4

    def test_most_linked_to_targets(self, gen):
        intercepts = gen.generate_intercepts()
        linked = [ic for ic in intercepts if ic.related_target_id is not None]
        assert len(linked) == 10

    def test_hours_received_increasing(self, gen):
        intercepts = gen.generate_intercepts()
        hours = [ic.hour_received for ic in intercepts]
        assert hours == sorted(hours)

    def test_intercept_01_accurate(self, gen):
        intercepts = gen.generate_intercepts()
        ic01 = [ic for ic in intercepts if ic.id == "intercept_01"][0]
        assert ic01.actually_accurate is True
        assert ic01.related_target_id == "target_01"

    def test_intercept_02_disinformation(self, gen):
        intercepts = gen.generate_intercepts()
        ic02 = [ic for ic in intercepts if ic.id == "intercept_02"][0]
        assert ic02.is_disinformation is True
        assert ic02.actually_accurate is False


# ── Generate Pressures ──────────────────────────────────────────────────


class TestGeneratePressures:

    def test_pressure_count(self, gen):
        pressures = gen.generate_pressures()
        assert len(pressures) == 8

    def test_unique_ids(self, gen):
        pressures = gen.generate_pressures()
        ids = [p.id for p in pressures]
        assert len(ids) == len(set(ids))

    def test_sources_varied(self, gen):
        pressures = gen.generate_pressures()
        sources = {p.source for p in pressures}
        assert PressureSource.POLITICAL in sources
        assert PressureSource.MILITARY_COMMAND in sources
        assert PressureSource.NGO in sources
        assert PressureSource.MEDIA in sources

    def test_all_have_demands(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert len(p.demand) > 0

    def test_all_have_descriptions(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert len(p.description) > 0

    def test_all_start_unresponded(self, gen):
        pressures = gen.generate_pressures()
        for p in pressures:
            assert p.responded is False
            assert p.complied is False

    def test_some_have_related_targets(self, gen):
        pressures = gen.generate_pressures()
        linked = [p for p in pressures if p.related_target_id is not None]
        assert len(linked) >= 5

    def test_hours_span_window(self, gen):
        pressures = gen.generate_pressures()
        hours = [p.hour_presented for p in pressures]
        assert min(hours) < 10
        assert max(hours) > 35

    def test_pressure_01_military(self, gen):
        pressures = gen.generate_pressures()
        p01 = [p for p in pressures if p.id == "pressure_01"][0]
        assert p01.source == PressureSource.MILITARY_COMMAND
        assert p01.related_target_id == "target_01"

    def test_pressure_05_sovereign(self, gen):
        pressures = gen.generate_pressures()
        p05 = [p for p in pressures if p.id == "pressure_05"][0]
        assert p05.source == PressureSource.POLITICAL
        assert p05.related_target_id == "target_10"


# ── Generate Weather Schedule ───────────────────────────────────────────


class TestGenerateWeatherSchedule:

    def test_covers_48_hours(self, gen):
        schedule = gen.generate_weather_schedule()
        assert len(schedule) == 48

    def test_keys_are_hours(self, gen):
        schedule = gen.generate_weather_schedule()
        for h in range(48):
            assert h in schedule

    def test_values_are_weather_conditions(self, gen):
        schedule = gen.generate_weather_schedule()
        for h, cond in schedule.items():
            assert isinstance(cond, WeatherCondition)

    def test_conditions_varied(self, gen):
        schedule = gen.generate_weather_schedule()
        conditions = set(schedule.values())
        assert len(conditions) >= 4

    def test_first_block_clear(self, gen):
        schedule = gen.generate_weather_schedule()
        for h in range(6):
            assert schedule[h] == WeatherCondition.CLEAR


# ── Generate All ────────────────────────────────────────────────────────


class TestGenerateAll:

    def test_returns_dict(self, gen):
        data = gen.generate_all()
        assert isinstance(data, dict)

    def test_has_all_keys(self, gen):
        data = gen.generate_all()
        assert "targets" in data
        assert "intercepts" in data
        assert "pressures" in data
        assert "weather_schedule" in data

    def test_targets_list(self, gen):
        data = gen.generate_all()
        assert len(data["targets"]) == 12

    def test_intercepts_list(self, gen):
        data = gen.generate_all()
        assert len(data["intercepts"]) == 10

    def test_pressures_list(self, gen):
        data = gen.generate_all()
        assert len(data["pressures"]) == 8


# ── Determinism ─────────────────────────────────────────────────────────


class TestDeterminism:

    def test_same_seed_same_targets(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        t1 = gen1.generate_targets()
        t2 = gen2.generate_targets()
        assert len(t1) == len(t2)
        for a, b in zip(t1, t2):
            assert a.id == b.id
            assert a.name == b.name
            assert a.zone == b.zone

    def test_same_seed_same_intercepts(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        i1 = gen1.generate_intercepts()
        i2 = gen2.generate_intercepts()
        assert len(i1) == len(i2)
        for a, b in zip(i1, i2):
            assert a.id == b.id
            assert a.content == b.content

    def test_same_seed_same_pressures(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        p1 = gen1.generate_pressures()
        p2 = gen2.generate_pressures()
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2):
            assert a.id == b.id
            assert a.demand == b.demand

    def test_same_seed_same_weather(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        w1 = gen1.generate_weather_schedule()
        w2 = gen2.generate_weather_schedule()
        assert w1 == w2
