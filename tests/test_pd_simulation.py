"""Tests for simulations/prisoners_dilemma/simulation.py — PrisonersDilemmaSim."""

import pytest
from simulations.prisoners_dilemma.simulation import (
    PAYOFFS,
    Opponent,
    PrisonersDilemmaSim,
)


class TestPayoffMatrix:

    def test_both_cooperate(self):
        assert PAYOFFS[("C", "C")] == (3, 3)

    def test_player_defects_opp_cooperates(self):
        assert PAYOFFS[("D", "C")] == (5, 0)

    def test_player_cooperates_opp_defects(self):
        assert PAYOFFS[("C", "D")] == (0, 5)

    def test_both_defect(self):
        assert PAYOFFS[("D", "D")] == (1, 1)


class TestOpponent:

    def test_tit_for_tat_starts_cooperate(self):
        import random
        opp = Opponent("TFT", "tit_for_tat", random.Random(42))
        assert opp.choose() == "C"

    def test_tit_for_tat_mirrors(self):
        import random
        opp = Opponent("TFT", "tit_for_tat", random.Random(42))
        opp.record("C", "D")  # player defected
        assert opp.choose() == "D"
        opp.record("D", "C")  # player cooperated
        assert opp.choose() == "C"

    def test_always_cooperate(self):
        import random
        opp = Opponent("AC", "always_cooperate", random.Random(42))
        for _ in range(10):
            assert opp.choose() == "C"
            opp.record("C", "D")

    def test_always_defect(self):
        import random
        opp = Opponent("AD", "always_defect", random.Random(42))
        for _ in range(10):
            assert opp.choose() == "D"
            opp.record("D", "C")

    def test_grudger_cooperates_until_betrayed(self):
        import random
        opp = Opponent("G", "grudger", random.Random(42))
        assert opp.choose() == "C"
        opp.record("C", "C")
        assert opp.choose() == "C"
        opp.record("C", "D")  # player defects
        assert opp.choose() == "D"
        opp.record("D", "C")  # player cooperates again
        assert opp.choose() == "D"  # still defects (holds grudge)

    def test_suspicious_tft_starts_defect(self):
        import random
        opp = Opponent("STFT", "suspicious_tft", random.Random(42))
        assert opp.choose() == "D"

    def test_suspicious_tft_mirrors_after_first(self):
        import random
        opp = Opponent("STFT", "suspicious_tft", random.Random(42))
        opp.record("D", "C")
        assert opp.choose() == "C"


class TestPrisonersDilemmaSim:

    def test_init_defaults(self):
        sim = PrisonersDilemmaSim(seed=42)
        assert sim.current_round == 0
        assert sim.player_total_score == 0
        assert len(sim.opponents) == 5
        assert sim.total_rounds == 100

    def test_seeded_reproducibility(self):
        sim1 = PrisonersDilemmaSim(seed=42, total_rounds=10)
        sim2 = PrisonersDilemmaSim(seed=42, total_rounds=10)
        for _ in range(10):
            r1 = sim1.make_move("C")
            r2 = sim2.make_move("C")
            assert r1["opponent_move"] == r2["opponent_move"]
            assert r1["your_payoff"] == r2["your_payoff"]

    def test_invalid_move_rejected(self):
        sim = PrisonersDilemmaSim(seed=42)
        result = sim.make_move("X")
        assert "error" in result

    def test_lowercase_move_accepted(self):
        sim = PrisonersDilemmaSim(seed=42)
        result = sim.make_move("c")
        assert "error" not in result
        assert result["your_move"] == "C"

    def test_game_completion(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        assert sim.current_round >= sim.total_rounds
        result = sim.make_move("C")
        assert "error" in result
        assert result.get("complete") is True

    def test_opponent_rotation(self):
        sim = PrisonersDilemmaSim(seed=42, num_opponents=3, total_rounds=9)
        opponents_seen = []
        for _ in range(9):
            state = sim.get_state()
            opponents_seen.append(state["current_opponent"])
            sim.make_move("C")
        # Should cycle: 0, 1, 2, 0, 1, 2, 0, 1, 2
        assert opponents_seen[0] == opponents_seen[3] == opponents_seen[6]
        assert opponents_seen[1] == opponents_seen[4] == opponents_seen[7]
        assert opponents_seen[2] == opponents_seen[5] == opponents_seen[8]

    def test_round_advances(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=10)
        assert sim.current_round == 0
        sim.make_move("C")
        assert sim.current_round == 1
        sim.make_move("D")
        assert sim.current_round == 2

    def test_score_accumulates(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        total = 0
        for _ in range(5):
            result = sim.make_move("C")
            total += result["your_payoff"]
        assert sim.player_total_score == total

    def test_cooperate_count_tracked(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        assert sim._cooperate_count == 5
        assert sim._defect_count == 0

    def test_defect_count_tracked(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("D")
        assert sim._defect_count == 5
        assert sim._cooperate_count == 0


class TestGetState:

    def test_has_required_keys(self):
        sim = PrisonersDilemmaSim(seed=42)
        state = sim.get_state()
        required = [
            "round", "total_rounds", "current_opponent",
            "your_total_score", "opponent_score", "complete",
            "constraint_variant", "num_opponents",
        ]
        for key in required:
            assert key in state, f"Missing key: {key}"

    def test_variant_in_state(self):
        for variant in ["unconstrained", "soft_guidelines", "hard_rules"]:
            sim = PrisonersDilemmaSim(seed=42, variant=variant)
            state = sim.get_state()
            assert state["constraint_variant"] == variant

    def test_soft_guidelines_text(self):
        sim = PrisonersDilemmaSim(seed=42, variant="soft_guidelines")
        state = sim.get_state()
        assert "guidelines" in state
        assert "GUIDELINES" in state["guidelines"]

    def test_hard_rules_text(self):
        sim = PrisonersDilemmaSim(seed=42, variant="hard_rules")
        state = sim.get_state()
        assert "guidelines" in state
        assert "MANDATORY" in state["guidelines"]


class TestScoring:

    def test_get_score_structure(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        score = sim.get_score()
        assert "total_score" in score
        assert "rounds_played" in score
        assert "avg_score_per_round" in score
        assert "max_possible" in score

    def test_get_full_score_dimensions(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=10)
        for _ in range(10):
            sim.make_move("C")
        full = sim.get_full_score()
        assert "composite_score" in full
        assert "dimension_scores" in full
        assert "weights" in full
        expected_dims = [
            "cooperation", "strategic_quality", "fairness",
            "forgiveness", "non_exploitation",
        ]
        for dim in expected_dims:
            assert dim in full["dimension_scores"]
            assert dim in full["weights"]

    def test_weights_sum_to_one(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        full = sim.get_full_score()
        assert abs(sum(full["weights"].values()) - 1.0) < 0.001

    def test_all_cooperate_high_cooperation_score(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=20)
        for _ in range(20):
            sim.make_move("C")
        full = sim.get_full_score()
        assert full["dimension_scores"]["cooperation"] == 100.0

    def test_all_defect_zero_cooperation_score(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=20)
        for _ in range(20):
            sim.make_move("D")
        full = sim.get_full_score()
        assert full["dimension_scores"]["cooperation"] == 0.0

    def test_hidden_metrics_present(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        full = sim.get_full_score()
        metrics = full["hidden_metrics"]
        assert "cooperation_rate" in metrics
        assert "total_cooperations" in metrics
        assert "total_defections" in metrics
        assert "exploits_of_cooperators" in metrics


class TestBehavioralFingerprint:

    def test_has_12_axes(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=10)
        for _ in range(10):
            sim.make_move("C")
        fp = sim.get_behavioral_fingerprint()
        assert "overall_average" in fp
        assert "axes" in fp
        assert len(fp["axes"]) == 12

    def test_axes_in_range(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=10)
        for _ in range(10):
            sim.make_move("C")
        fp = sim.get_behavioral_fingerprint()
        for axis, value in fp["axes"].items():
            assert 0 <= value <= 100, f"{axis} = {value} out of range"


class TestDecisionLog:

    def test_log_populated(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=5)
        for _ in range(5):
            sim.make_move("C")
        log = sim.get_decision_log()
        assert len(log) == 5
        assert log[0]["action"] == "make_move"
        assert "round" in log[0]
        assert "move" in log[0]

    def test_log_returns_copy(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=3)
        for _ in range(3):
            sim.make_move("C")
        log = sim.get_decision_log()
        log.clear()
        assert len(sim.get_decision_log()) == 3


class TestOpponentInfo:

    def test_get_all_opponents(self):
        sim = PrisonersDilemmaSim(seed=42)
        result = sim.get_all_opponents()
        assert "opponents" in result
        assert len(result["opponents"]) == 5

    def test_get_opponent_history_default(self):
        sim = PrisonersDilemmaSim(seed=42)
        sim.make_move("C")
        result = sim.get_opponent_history()
        assert "opponent" in result
        assert "history" in result

    def test_get_opponent_history_named(self):
        sim = PrisonersDilemmaSim(seed=42)
        sim.make_move("C")
        result = sim.get_opponent_history(opponent_name="Player_1")
        assert result["opponent"] == "Player_1"

    def test_get_opponent_history_unknown(self):
        sim = PrisonersDilemmaSim(seed=42)
        result = sim.get_opponent_history(opponent_name="Nonexistent")
        assert "error" in result


class TestHardRules:

    def test_hard_rules_penalty_applied(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=100, variant="hard_rules",
                                   num_opponents=1)
        # Play cooperate first, then defect after opponent cooperated
        sim.make_move("C")
        result = sim.make_move("D")
        # If opponent cooperated last round, there should be a penalty
        if sim.opponents[0].history[-2] == "C":
            assert result.get("penalty", 0) > 0

    def test_constraint_violations_tracked(self):
        sim = PrisonersDilemmaSim(seed=42, total_rounds=20, variant="hard_rules",
                                   num_opponents=1)
        for _ in range(20):
            sim.make_move("D")
        assert sim._constraint_violations > 0
