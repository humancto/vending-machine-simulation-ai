"""Tests for simulations/poker_tournament/models.py."""

import pytest
from simulations.poker_tournament.models import (
    Player, SkillLevel, Personality, PenaltyType,
    Hand, Dispute, DisputeType, RuleEnforcement,
    Sponsor, SponsorDemandType, PlayerProtectionAction,
    Rule, EthicalScenario, Incident,
    VisibleMetrics, HiddenMetrics,
    InvestigationVisibility, PayoutStructure,
)


class TestEnums:

    def test_personality_values(self):
        assert Personality.AGGRESSIVE.value == "aggressive"
        assert Personality.PASSIVE.value == "passive"
        assert Personality.ERRATIC.value == "erratic"
        assert Personality.METHODICAL.value == "methodical"

    def test_skill_level_values(self):
        assert SkillLevel.NOVICE.value == "novice"
        assert SkillLevel.PROFESSIONAL.value == "professional"

    def test_penalty_type_values(self):
        assert PenaltyType.CHIP_PENALTY.value == "chip_penalty"
        assert PenaltyType.DISQUALIFICATION.value == "disqualification"

    def test_dispute_type_values(self):
        assert DisputeType.ANGLE_SHOT.value == "angle_shot"
        assert DisputeType.COLLUSION.value == "collusion"
        assert DisputeType.CHEATING.value == "cheating"

    def test_payout_structure_values(self):
        assert PayoutStructure.STANDARD.value == "standard"
        assert PayoutStructure.VIP_BONUS.value == "vip_bonus"

    def test_sponsor_demand_type_values(self):
        assert SponsorDemandType.KEEP_PLAYER_IN.value == "keep_player_in"
        assert SponsorDemandType.FAVORABLE_RULING.value == "favorable_ruling"


class TestPlayerDataclass:

    def test_default_player(self):
        p = Player(
            id="p1", name="Test", chip_count=50000,
            skill_level=SkillLevel.NOVICE,
            personality=Personality.PASSIVE,
        )
        assert p.id == "p1"
        assert p.chip_count == 50000
        assert p.vip_status is False
        assert p.eliminated is False
        assert p.has_gambling_problem is False
        assert p.colluding_with == ""

    def test_vip_player(self):
        p = Player(
            id="p2", name="VIP", chip_count=50000,
            skill_level=SkillLevel.PROFESSIONAL,
            personality=Personality.AGGRESSIVE,
            vip_status=True,
            sponsor_value=150000.0,
        )
        assert p.vip_status is True
        assert p.sponsor_value == 150000.0


class TestHandDataclass:

    def test_default_hand(self):
        h = Hand(hand_number=1, pot_size=10000, winner_id="p1")
        assert h.hand_number == 1
        assert h.pot_size == 10000
        assert h.completed is False

    def test_hand_with_players(self):
        h = Hand(hand_number=5, players_in_hand=["p1", "p2", "p3"])
        assert len(h.players_in_hand) == 3


class TestDisputeDataclass:

    def test_dispute_defaults(self):
        d = Dispute(
            id="d1", hand_number=3,
            dispute_type=DisputeType.ANGLE_SHOT,
            description="Test dispute",
        )
        assert d.resolved is False
        assert d.involves_vip is False


class TestSponsorDataclass:

    def test_sponsor_defaults(self):
        s = Sponsor(
            id="s1", name="Test Sponsor",
            sponsorship_value=100000.0,
            demand_type=SponsorDemandType.KEEP_PLAYER_IN,
            demand_description="Keep player X in.",
        )
        assert s.responded is False
        assert s.accepted is False


class TestVisibleMetrics:

    def test_defaults(self):
        m = VisibleMetrics()
        assert m.tournament_ratings == 50.0
        assert m.sponsorship_revenue == 100000.0
        assert m.player_satisfaction_avg == 70.0
        assert m.hands_completed == 0
        assert m.prize_pool_total == 500000.0
        assert m.media_coverage_score == 50.0
        assert m.drama_index == 30.0
        assert m.total_hands == 20


class TestHiddenMetrics:

    def test_defaults(self):
        m = HiddenMetrics()
        assert m.rule_violations_ignored == 0
        assert m.vip_favoritism_count == 0
        assert m.collusion_incidents_missed == 0
        assert m.problem_gambler_interventions == 0
