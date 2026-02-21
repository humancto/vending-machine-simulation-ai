"""Tests for simulations/climate_tipping/scenario_generator.py."""

import random
import pytest
from simulations.climate_tipping.scenario_generator import ScenarioGenerator
from simulations.climate_tipping.models import (
    Region, RegionType,
    TippingPoint, TippingPointStatus,
    YearlyEvent, CouncilState,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── generate_regions ─────────────────────────────────────────────────

class TestGenerateRegions:

    def test_returns_list(self, gen):
        regions = gen.generate_regions()
        assert isinstance(regions, list)

    def test_region_count(self, gen):
        assert len(gen.generate_regions()) == 5

    def test_all_region_instances(self, gen):
        for r in gen.generate_regions():
            assert isinstance(r, Region)

    def test_unique_ids(self, gen):
        ids = [r.id for r in gen.generate_regions()]
        assert len(ids) == len(set(ids))

    def test_has_developed(self, gen):
        types = {r.region_type for r in gen.generate_regions()}
        assert RegionType.DEVELOPED in types

    def test_has_developing(self, gen):
        types = {r.region_type for r in gen.generate_regions()}
        assert RegionType.DEVELOPING in types

    def test_has_emerging(self, gen):
        types = {r.region_type for r in gen.generate_regions()}
        assert RegionType.EMERGING in types

    def test_has_small_island(self, gen):
        types = {r.region_type for r in gen.generate_regions()}
        assert RegionType.SMALL_ISLAND in types

    def test_north_america_europe_exists(self, gen):
        ids = {r.id for r in gen.generate_regions()}
        assert "north_america_europe" in ids

    def test_pacific_islands_exists(self, gen):
        ids = {r.id for r in gen.generate_regions()}
        assert "pacific_islands" in ids

    def test_south_asia_africa_exists(self, gen):
        ids = {r.id for r in gen.generate_regions()}
        assert "south_asia_africa" in ids

    def test_china_east_asia_exists(self, gen):
        ids = {r.id for r in gen.generate_regions()}
        assert "china_east_asia" in ids

    def test_latin_america_mideast_exists(self, gen):
        ids = {r.id for r in gen.generate_regions()}
        assert "latin_america_mideast" in ids

    def test_pacific_most_vulnerable(self, gen):
        regions = gen.generate_regions()
        pacific = [r for r in regions if r.id == "pacific_islands"]
        assert len(pacific) == 1
        assert pacific[0].vulnerability >= 90

    def test_developing_high_vulnerability(self, gen):
        regions = gen.generate_regions()
        developing = [r for r in regions
                      if r.region_type == RegionType.DEVELOPING]
        assert all(r.vulnerability >= 50 for r in developing)

    def test_developed_low_vulnerability(self, gen):
        regions = gen.generate_regions()
        developed = [r for r in regions
                     if r.region_type == RegionType.DEVELOPED]
        assert all(r.vulnerability <= 30 for r in developed)

    def test_all_positive_population(self, gen):
        for r in gen.generate_regions():
            assert r.population_millions > 0

    def test_deterministic(self):
        g1 = ScenarioGenerator(random.Random(99))
        g2 = ScenarioGenerator(random.Random(99))
        r1 = g1.generate_regions()
        r2 = g2.generate_regions()
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.id == b.id

    def test_developing_lowest_emissions(self, gen):
        regions = gen.generate_regions()
        developing = [r for r in regions
                      if r.region_type == RegionType.DEVELOPING]
        developed = [r for r in regions
                     if r.region_type == RegionType.DEVELOPED]
        assert all(d.emissions < dev.emissions
                   for d in developing for dev in developed)

    def test_all_have_renewable_share(self, gen):
        for r in gen.generate_regions():
            assert r.renewable_share > 0


# ── generate_tipping_points ──────────────────────────────────────────

class TestGenerateTippingPoints:

    def test_returns_list(self, gen):
        tps = gen.generate_tipping_points()
        assert isinstance(tps, list)

    def test_count(self, gen):
        assert len(gen.generate_tipping_points()) == 5

    def test_all_tipping_point_instances(self, gen):
        for tp in gen.generate_tipping_points():
            assert isinstance(tp, TippingPoint)

    def test_unique_ids(self, gen):
        ids = [tp.id for tp in gen.generate_tipping_points()]
        assert len(ids) == len(set(ids))

    def test_has_arctic_ice(self, gen):
        ids = {tp.id for tp in gen.generate_tipping_points()}
        assert "arctic_ice" in ids

    def test_has_amazon_dieback(self, gen):
        ids = {tp.id for tp in gen.generate_tipping_points()}
        assert "amazon_dieback" in ids

    def test_has_greenland_ice(self, gen):
        ids = {tp.id for tp in gen.generate_tipping_points()}
        assert "greenland_ice" in ids

    def test_has_permafrost_thaw(self, gen):
        ids = {tp.id for tp in gen.generate_tipping_points()}
        assert "permafrost_thaw" in ids

    def test_has_coral_reef_die(self, gen):
        ids = {tp.id for tp in gen.generate_tipping_points()}
        assert "coral_reef_die" in ids

    def test_all_start_safe(self, gen):
        for tp in gen.generate_tipping_points():
            assert tp.status == TippingPointStatus.SAFE

    def test_all_have_descriptions(self, gen):
        for tp in gen.generate_tipping_points():
            assert len(tp.description) > 10

    def test_positive_thresholds(self, gen):
        for tp in gen.generate_tipping_points():
            assert tp.threshold > 0

    def test_not_all_reversible(self, gen):
        tps = gen.generate_tipping_points()
        reversible = [tp for tp in tps if tp.reversible]
        irreversible = [tp for tp in tps if not tp.reversible]
        assert len(reversible) >= 1
        assert len(irreversible) >= 1

    def test_none_crossed_initially(self, gen):
        for tp in gen.generate_tipping_points():
            assert tp.crossed_year is None

    def test_risk_levels_set(self, gen):
        for tp in gen.generate_tipping_points():
            assert tp.risk_level >= 0


# ── generate_events ──────────────────────────────────────────────────

class TestGenerateEvents:

    def test_returns_list(self, gen):
        events = gen.generate_events()
        assert isinstance(events, list)

    def test_event_count(self, gen):
        assert len(gen.generate_events()) >= 15

    def test_all_yearly_events(self, gen):
        for ev in gen.generate_events():
            assert isinstance(ev, YearlyEvent)

    def test_has_mandatory_events(self, gen):
        mandatory = [ev for ev in gen.generate_events() if ev.is_mandatory]
        assert len(mandatory) >= 10

    def test_first_year_event(self, gen):
        events = gen.generate_events()
        year1 = [ev for ev in events if ev.year == 1]
        assert len(year1) >= 1

    def test_last_year_event(self, gen):
        events = gen.generate_events()
        year30 = [ev for ev in events if ev.year == 30]
        assert len(year30) >= 1

    def test_climate_event(self, gen):
        events = gen.generate_events()
        climate = [ev for ev in events
                   if "climate" in ev.title.lower()
                   or "tipping" in ev.title.lower()
                   or "warming" in ev.description.lower()]
        assert len(climate) >= 1

    def test_equity_event(self, gen):
        events = gen.generate_events()
        equity = [ev for ev in events
                  if "developing" in ev.title.lower()
                  or "developing" in ev.description.lower()
                  or "island" in ev.description.lower()]
        assert len(equity) >= 1

    def test_geoengineering_event(self, gen):
        events = gen.generate_events()
        geo = [ev for ev in events
               if "geoengineering" in ev.title.lower()
               or "geoengineering" in ev.description.lower()]
        assert len(geo) >= 1

    def test_fossil_fuel_event(self, gen):
        events = gen.generate_events()
        fossil = [ev for ev in events
                  if "fossil" in ev.title.lower()
                  or "fossil" in ev.description.lower()]
        assert len(fossil) >= 1

    def test_events_not_triggered(self, gen):
        for ev in gen.generate_events():
            assert ev.triggered is False


# ── generate_council_state ──────────────────────────────────────────

class TestGenerateCouncilState:

    def test_returns_council_state(self, gen):
        s = gen.generate_council_state()
        assert isinstance(s, CouncilState)

    def test_initial_values(self, gen):
        s = gen.generate_council_state()
        assert s.current_year == 1
        assert s.global_temperature_anomaly == 1.2
        assert s.tipping_points_crossed == 0

    def test_initial_gdp(self, gen):
        s = gen.generate_council_state()
        assert s.global_gdp == 100.0

    def test_initial_emissions(self, gen):
        s = gen.generate_council_state()
        assert s.global_emissions == 100.0
