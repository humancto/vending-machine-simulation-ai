"""Tests for simulations/auction_house/models.py."""

import pytest
from simulations.auction_house.models import (
    LotCategory, ProvenanceStatus, AuthenticationLevel,
    AuthenticationResult, BidderExpertise, ConsignorType,
    CulturalSignificance, Lot, Bidder, Consignor,
    SpecialScenario, VisibleMetrics,
)


class TestEnums:

    def test_lot_categories(self):
        assert LotCategory.PAINTING.value == "painting"
        assert LotCategory.ANTIQUITY.value == "antiquity"
        assert len(LotCategory) == 6

    def test_provenance_statuses(self):
        assert ProvenanceStatus.CLEAN.value == "clean"
        assert ProvenanceStatus.SUSPICIOUS.value == "suspicious"
        assert len(ProvenanceStatus) == 4

    def test_authentication_levels(self):
        assert AuthenticationLevel.NONE.value == "none"
        assert AuthenticationLevel.EXPERT.value == "expert"
        assert len(AuthenticationLevel) == 4

    def test_authentication_results(self):
        assert AuthenticationResult.PENDING.value == "pending"
        assert AuthenticationResult.FORGERY.value == "forgery"
        assert len(AuthenticationResult) == 4

    def test_bidder_expertise(self):
        assert BidderExpertise.NOVICE.value == "novice"
        assert BidderExpertise.EXPERT.value == "expert"
        assert len(BidderExpertise) == 3

    def test_consignor_types(self):
        assert ConsignorType.ESTATE_EXECUTOR.value == "estate_executor"
        assert ConsignorType.DEALER.value == "dealer"
        assert len(ConsignorType) == 4

    def test_cultural_significance(self):
        assert CulturalSignificance.NONE.value == "none"
        assert CulturalSignificance.NATIONAL_TREASURE.value == "national_treasure"
        assert len(CulturalSignificance) == 5


class TestLot:

    def test_default_lot(self):
        lot = Lot(id="test", name="Test Lot",
                  category=LotCategory.PAINTING,
                  estimated_value=100_000)
        assert lot.id == "test"
        assert lot.reserve_price == 0.0
        assert lot.authentication_status == AuthenticationResult.PENDING
        assert lot.sold is False
        assert lot.is_forged is False

    def test_lot_with_values(self):
        lot = Lot(id="x", name="X",
                  category=LotCategory.ANTIQUITY,
                  estimated_value=500_000,
                  provenance=ProvenanceStatus.SUSPICIOUS,
                  is_looted=True,
                  true_value=500_000)
        assert lot.is_looted is True
        assert lot.provenance == ProvenanceStatus.SUSPICIOUS


class TestBidder:

    def test_default_bidder(self):
        b = Bidder(id="b1", name="Test",
                   budget=1_000_000,
                   expertise_level=BidderExpertise.EXPERT)
        assert b.vip_status is False
        assert b.banned is False
        assert b.is_colluding is False

    def test_colluding_bidder(self):
        b = Bidder(id="b1", name="Test",
                   budget=500_000,
                   expertise_level=BidderExpertise.INTERMEDIATE,
                   is_colluding=True,
                   collusion_partners=["b2", "b3"])
        assert b.is_colluding is True
        assert len(b.collusion_partners) == 2


class TestConsignor:

    def test_default_consignor(self):
        c = Consignor(id="c1", name="Test",
                      consignor_type=ConsignorType.DEALER)
        assert c.naive_about_value is False
        assert c.trying_to_pass_fake is False

    def test_naive_consignor(self):
        c = Consignor(id="c1", name="Widow",
                      consignor_type=ConsignorType.ESTATE_EXECUTOR,
                      naive_about_value=True)
        assert c.naive_about_value is True


class TestVisibleMetrics:

    def test_defaults(self):
        m = VisibleMetrics()
        assert m.total_commission == 0.0
        assert m.hammer_price_total == 0.0
        assert m.lots_sold == 0
        assert m.client_satisfaction == 75.0
        assert m.house_reputation == 80.0
        assert m.total_sessions == 10
