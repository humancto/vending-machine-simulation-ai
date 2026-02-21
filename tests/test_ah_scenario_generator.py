"""Tests for simulations/auction_house/scenario_generator.py."""

import random
import pytest
from simulations.auction_house.scenario_generator import ScenarioGenerator


class TestScenarioGenerator:

    def test_generate_all_keys(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert "lots" in data
        assert "bidders" in data
        assert "consignors" in data
        assert "ethical_scenarios" in data

    def test_thirty_lots(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["lots"]) == 30

    def test_fifteen_bidders(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["bidders"]) == 15

    def test_ten_consignors(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["consignors"]) == 10

    def test_ten_ethical_scenarios(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["ethical_scenarios"]) == 10

    def test_lots_have_sessions_1_to_10(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        sessions = {lot.session_number for lot in data["lots"]}
        assert sessions == set(range(1, 11))

    def test_three_lots_per_session(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for session in range(1, 11):
            count = sum(1 for lot in data["lots"]
                        if lot.session_number == session)
            assert count == 3, f"Session {session} has {count} lots"

    def test_scenarios_have_unique_sessions(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        sessions = [s.session for s in data["ethical_scenarios"]]
        assert len(sessions) == len(set(sessions))

    def test_some_lots_are_forged(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        forged = [lot for lot in data["lots"] if lot.is_forged]
        assert len(forged) >= 2

    def test_some_lots_are_looted(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        looted = [lot for lot in data["lots"] if lot.is_looted]
        assert len(looted) >= 2

    def test_some_bidders_are_colluding(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        colluding = [b for b in data["bidders"] if b.is_colluding]
        assert len(colluding) == 3

    def test_some_consignors_naive(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        naive = [c for c in data["consignors"]
                 if c.naive_about_value]
        assert len(naive) >= 2

    def test_consignor_lots_populated(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for consignor in data["consignors"]:
            if consignor.id in ("con_01", "con_02"):
                assert len(consignor.lots) > 0

    def test_seed_determinism(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        assert len(data1["lots"]) == len(data2["lots"])
        for i in range(len(data1["lots"])):
            assert data1["lots"][i].id == data2["lots"][i].id
            assert data1["lots"][i].name == data2["lots"][i].name
