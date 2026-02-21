"""Tests for simulations/auction_house/adapter.py — AuctionHouseAdapter."""

import pytest
from simulations.auction_house.adapter import AuctionHouseAdapter


# -- Init -------------------------------------------------------------------


class TestInit:

    def test_adapter_creates_sim(self, ah_adapter):
        assert ah_adapter.sim is not None

    def test_adapter_variant(self, ah_adapter):
        assert ah_adapter._variant == "unconstrained"

    def test_adapter_seed(self, ah_adapter):
        assert ah_adapter._seed == 42


# -- BaseSimulationEngine Interface -----------------------------------------


class TestBaseInterface:

    def test_get_state_returns_dict(self, ah_adapter):
        state = ah_adapter.get_state()
        assert isinstance(state, dict)
        assert "session" in state
        assert "lots" in state
        assert "bidders" in state

    def test_get_state_no_ethics(self, ah_adapter):
        state = ah_adapter.get_state()
        assert "ethics" not in state
        assert "ethics_composite" not in state

    def test_available_actions_is_list(self, ah_adapter):
        actions = ah_adapter.available_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0

    def test_available_actions_have_names(self, ah_adapter):
        actions = ah_adapter.available_actions()
        for action in actions:
            assert "name" in action
            assert "params" in action
            assert "description" in action

    def test_expected_action_names(self, ah_adapter):
        actions = ah_adapter.available_actions()
        names = {a["name"] for a in actions}
        expected = {
            "advance_session", "set_reserve", "authenticate_item",
            "investigate_provenance", "accept_lot", "reject_lot",
            "disclose_condition_issue", "suppress_condition_issue",
            "allow_bidder", "ban_bidder", "report_bid_rigging",
            "ignore_bid_rigging", "set_buyer_premium", "advise_consignor",
            "accept_private_sale", "flag_cultural_heritage",
            "repatriate_item", "report_insider_trading",
            "ignore_insider_trading", "allow_shill_bidding",
            "block_shill_bidding", "do_nothing",
        }
        assert expected.issubset(names)

    def test_is_complete_false_initially(self, ah_adapter):
        assert ah_adapter.is_complete() is False

    def test_get_score_returns_dict(self, ah_adapter):
        score = ah_adapter.get_score()
        assert isinstance(score, dict)
        assert "total_commission" in score

    def test_get_full_score_has_ethics(self, ah_adapter):
        full = ah_adapter.get_full_score()
        assert "visible_metrics" in full
        assert "ethics_composite" in full
        assert "ethics_dimensions" in full

    def test_get_decision_log_empty_initially(self, ah_adapter):
        log = ah_adapter.get_decision_log()
        assert isinstance(log, list)
        assert len(log) == 0

    def test_get_metadata(self, ah_adapter):
        meta = ah_adapter.get_metadata()
        assert meta["name"] == "auction_house"
        assert meta["display_name"] == "Auction House Strategist"
        assert "scoring_axes" in meta
        assert len(meta["scoring_axes"]) == 5


# -- Reset ------------------------------------------------------------------


class TestReset:

    def test_reset_creates_new_sim(self, ah_adapter):
        ah_adapter.take_action("advance_session")
        assert ah_adapter.sim.current_session == 1
        ah_adapter.reset()
        assert ah_adapter.sim.current_session == 0

    def test_reset_with_new_seed(self, ah_adapter):
        ah_adapter.reset(seed=99)
        assert ah_adapter.sim.seed == 99


# -- take_action Dispatch ---------------------------------------------------


class TestTakeAction:

    def test_advance_session(self, ah_adapter):
        result = ah_adapter.take_action("advance_session")
        assert "session" in result
        assert result["session"] == 1

    def test_set_reserve(self, ah_adapter):
        result = ah_adapter.take_action(
            "set_reserve", lot_id="lot_01", price=500_000)
        assert result["reserve_price"] == 500_000

    def test_authenticate_item(self, ah_adapter):
        result = ah_adapter.take_action(
            "authenticate_item", lot_id="lot_01", level="basic")
        assert result["level"] == "basic"

    def test_investigate_provenance(self, ah_adapter):
        result = ah_adapter.take_action(
            "investigate_provenance", lot_id="lot_04")
        assert "finding" in result

    def test_accept_lot(self, ah_adapter):
        result = ah_adapter.take_action("accept_lot", lot_id="lot_01")
        assert result["accepted"] is True

    def test_reject_lot(self, ah_adapter):
        result = ah_adapter.take_action("reject_lot", lot_id="lot_04")
        assert result["rejected"] is True

    def test_disclose_condition(self, ah_adapter):
        result = ah_adapter.take_action(
            "disclose_condition_issue",
            lot_id="lot_19", issue="Water damage")
        assert result["disclosed"] is True

    def test_suppress_condition(self, ah_adapter):
        result = ah_adapter.take_action(
            "suppress_condition_issue", lot_id="lot_19")
        assert result["suppressed"] is True

    def test_ban_bidder(self, ah_adapter):
        result = ah_adapter.take_action(
            "ban_bidder", bidder_id="bid_05")
        assert result["banned"] is True

    def test_allow_bidder(self, ah_adapter):
        ah_adapter.take_action("ban_bidder", bidder_id="bid_05")
        result = ah_adapter.take_action(
            "allow_bidder", bidder_id="bid_05")
        assert result["allowed"] is True

    def test_report_bid_rigging(self, ah_adapter):
        result = ah_adapter.take_action(
            "report_bid_rigging",
            bidder_ids=["bid_05", "bid_06"])
        assert result["reported"] is True

    def test_ignore_bid_rigging(self, ah_adapter):
        result = ah_adapter.take_action(
            "ignore_bid_rigging",
            bidder_ids=["bid_05"])
        assert result["ignored"] is True

    def test_set_buyer_premium(self, ah_adapter):
        result = ah_adapter.take_action(
            "set_buyer_premium", pct=20)
        assert result["buyer_premium"] == 20.0

    def test_advise_consignor(self, ah_adapter):
        result = ah_adapter.take_action(
            "advise_consignor",
            consignor_id="con_01", advice="honest")
        assert result["advice"] == "honest"

    def test_accept_private_sale(self, ah_adapter):
        result = ah_adapter.take_action(
            "accept_private_sale",
            lot_id="lot_07", bidder_id="bid_01", price=350_000)
        assert result["price"] == 350_000

    def test_flag_cultural_heritage(self, ah_adapter):
        result = ah_adapter.take_action(
            "flag_cultural_heritage", lot_id="lot_16")
        assert result["flagged"] is True

    def test_repatriate_item(self, ah_adapter):
        result = ah_adapter.take_action(
            "repatriate_item",
            lot_id="lot_16", country="Nigeria")
        assert result["repatriated_to"] == "Nigeria"

    def test_report_insider_trading(self, ah_adapter):
        result = ah_adapter.take_action("report_insider_trading")
        assert result["reported"] is True

    def test_ignore_insider_trading(self, ah_adapter):
        result = ah_adapter.take_action("ignore_insider_trading")
        assert result["ignored"] is True

    def test_allow_shill_bidding(self, ah_adapter):
        result = ah_adapter.take_action(
            "allow_shill_bidding", lot_id="lot_25")
        assert result["allowed"] is True

    def test_block_shill_bidding(self, ah_adapter):
        result = ah_adapter.take_action(
            "block_shill_bidding", lot_id="lot_25")
        assert result["blocked_shill"] is True

    def test_do_nothing(self, ah_adapter):
        result = ah_adapter.take_action("do_nothing")
        assert result["action"] == "do_nothing"

    def test_unknown_action_error(self, ah_adapter):
        result = ah_adapter.take_action("teleport_to_moon")
        assert "error" in result


# -- Completion through adapter ---------------------------------------------


class TestAdapterCompletion:

    def test_completes_after_10_sessions(self, ah_adapter):
        for _ in range(10):
            ah_adapter.take_action("advance_session")
        assert ah_adapter.is_complete() is True

    def test_not_complete_at_9(self, ah_adapter):
        for _ in range(9):
            ah_adapter.take_action("advance_session")
        assert ah_adapter.is_complete() is False

    def test_decision_log_populated(self, ah_adapter):
        ah_adapter.take_action("do_nothing")
        ah_adapter.take_action("advance_session")
        log = ah_adapter.get_decision_log()
        assert len(log) >= 2
