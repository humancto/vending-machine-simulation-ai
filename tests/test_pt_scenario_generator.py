"""Tests for simulations/poker_tournament/scenario_generator.py."""

import random
import pytest
from simulations.poker_tournament.scenario_generator import ScenarioGenerator


class TestScenarioGenerator:

    def test_generate_all_keys(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        expected_keys = {
            "players", "hands", "sponsors", "disputes",
            "rules", "ethical_scenarios", "incidents",
        }
        assert set(data.keys()) == expected_keys

    def test_eight_players(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["players"]) == 8

    def test_twenty_hands(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["hands"]) == 20

    def test_three_sponsors(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["sponsors"]) == 3

    def test_six_disputes(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["disputes"]) == 6

    def test_six_rules(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["rules"]) == 6

    def test_ten_ethical_scenarios(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["ethical_scenarios"]) == 10

    def test_four_incidents(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["incidents"]) == 4

    def test_players_have_colluding_pair(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        colluding = [p for p in data["players"] if p.colluding_with]
        assert len(colluding) == 2

    def test_players_have_problem_gambler(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        gamblers = [p for p in data["players"] if p.has_gambling_problem]
        assert len(gamblers) >= 1

    def test_players_have_angle_shooter(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        shooters = [p for p in data["players"]
                    if p.known_for_angle_shooting]
        assert len(shooters) >= 1

    def test_vip_players_exist(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        vips = [p for p in data["players"] if p.vip_status]
        assert len(vips) >= 2

    def test_seed_determinism(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        assert len(data1["players"]) == len(data2["players"])
        for p1, p2 in zip(data1["players"], data2["players"]):
            assert p1.id == p2.id
            assert p1.name == p2.name

    def test_hands_have_winners(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for hand in data["hands"]:
            assert hand.winner_id != ""

    def test_ethical_scenarios_at_odd_hands(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        hands = [s.hand_number for s in data["ethical_scenarios"]]
        # Scenarios at hands 1, 3, 5, 7, 9, 11, 13, 15, 17, 19
        expected = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        assert hands == expected
