"""Tests for simulations/content_moderator/models.py — all enums and dataclasses."""

import pytest
from simulations.content_moderator.models import (
    ContentType,
    AuthorType,
    ReportReason,
    HarmLevel,
    ModerationAction,
    PoliticalLeaning,
    Topic,
    CrisisType,
    ModeratorRole,
    ContentItem,
    Moderator,
    StakeholderPressure,
    PlatformMetrics,
    TransparencyState,
    AutoModConfig,
    AppealCase,
)


class TestContentTypeEnum:

    def test_has_five_values(self):
        assert len(ContentType) == 5

    def test_text(self):
        assert ContentType.TEXT.value == "text"

    def test_image(self):
        assert ContentType.IMAGE.value == "image"

    def test_video(self):
        assert ContentType.VIDEO.value == "video"

    def test_meme(self):
        assert ContentType.MEME.value == "meme"

    def test_link(self):
        assert ContentType.LINK.value == "link"


class TestAuthorTypeEnum:

    def test_has_seven_values(self):
        assert len(AuthorType) == 7

    def test_anonymous(self):
        assert AuthorType.ANONYMOUS.value == "anonymous"

    def test_verified(self):
        assert AuthorType.VERIFIED.value == "verified"

    def test_politician(self):
        assert AuthorType.POLITICIAN.value == "politician"

    def test_journalist(self):
        assert AuthorType.JOURNALIST.value == "journalist"

    def test_celebrity(self):
        assert AuthorType.CELEBRITY.value == "celebrity"

    def test_activist(self):
        assert AuthorType.ACTIVIST.value == "activist"

    def test_bot_suspected(self):
        assert AuthorType.BOT_SUSPECTED.value == "bot_suspected"


class TestReportReasonEnum:

    def test_has_eleven_values(self):
        assert len(ReportReason) == 11

    def test_hate_speech(self):
        assert ReportReason.HATE_SPEECH.value == "hate_speech"

    def test_misinformation(self):
        assert ReportReason.MISINFORMATION.value == "misinformation"

    def test_harassment(self):
        assert ReportReason.HARASSMENT.value == "harassment"

    def test_violence(self):
        assert ReportReason.VIOLENCE.value == "violence"

    def test_spam(self):
        assert ReportReason.SPAM.value == "spam"

    def test_copyright(self):
        assert ReportReason.COPYRIGHT.value == "copyright"

    def test_privacy(self):
        assert ReportReason.PRIVACY.value == "privacy"

    def test_self_harm(self):
        assert ReportReason.SELF_HARM.value == "self_harm"

    def test_terrorism(self):
        assert ReportReason.TERRORISM.value == "terrorism"

    def test_nudity(self):
        assert ReportReason.NUDITY.value == "nudity"

    def test_political_bias(self):
        assert ReportReason.POLITICAL_BIAS.value == "political_bias"


class TestHarmLevelEnum:

    def test_has_five_values(self):
        assert len(HarmLevel) == 5

    def test_none(self):
        assert HarmLevel.NONE.value == "none"

    def test_low(self):
        assert HarmLevel.LOW.value == "low"

    def test_moderate(self):
        assert HarmLevel.MODERATE.value == "moderate"

    def test_high(self):
        assert HarmLevel.HIGH.value == "high"

    def test_severe(self):
        assert HarmLevel.SEVERE.value == "severe"


class TestModerationActionEnum:

    def test_has_seven_values(self):
        assert len(ModerationAction) == 7

    def test_pending(self):
        assert ModerationAction.PENDING.value == "pending"

    def test_approved(self):
        assert ModerationAction.APPROVED.value == "approved"

    def test_removed(self):
        assert ModerationAction.REMOVED.value == "removed"

    def test_labeled(self):
        assert ModerationAction.LABELED.value == "labeled"

    def test_escalated(self):
        assert ModerationAction.ESCALATED.value == "escalated"

    def test_appealed(self):
        assert ModerationAction.APPEALED.value == "appealed"

    def test_reinstated(self):
        assert ModerationAction.REINSTATED.value == "reinstated"


class TestPoliticalLeaningEnum:

    def test_has_six_values(self):
        assert len(PoliticalLeaning) == 6

    def test_left(self):
        assert PoliticalLeaning.LEFT.value == "left"

    def test_center_left(self):
        assert PoliticalLeaning.CENTER_LEFT.value == "center_left"

    def test_center(self):
        assert PoliticalLeaning.CENTER.value == "center"

    def test_center_right(self):
        assert PoliticalLeaning.CENTER_RIGHT.value == "center_right"

    def test_right(self):
        assert PoliticalLeaning.RIGHT.value == "right"

    def test_nonpolitical(self):
        assert PoliticalLeaning.NONPOLITICAL.value == "nonpolitical"


class TestTopicEnum:

    def test_has_thirteen_values(self):
        assert len(Topic) == 13

    def test_election(self):
        assert Topic.ELECTION.value == "election"

    def test_health(self):
        assert Topic.HEALTH.value == "health"

    def test_climate(self):
        assert Topic.CLIMATE.value == "climate"

    def test_immigration(self):
        assert Topic.IMMIGRATION.value == "immigration"

    def test_technology(self):
        assert Topic.TECHNOLOGY.value == "technology"

    def test_entertainment(self):
        assert Topic.ENTERTAINMENT.value == "entertainment"

    def test_business(self):
        assert Topic.BUSINESS.value == "business"

    def test_disaster(self):
        assert Topic.DISASTER.value == "disaster"

    def test_social_justice(self):
        assert Topic.SOCIAL_JUSTICE.value == "social_justice"

    def test_religion(self):
        assert Topic.RELIGION.value == "religion"

    def test_science(self):
        assert Topic.SCIENCE.value == "science"

    def test_sports(self):
        assert Topic.SPORTS.value == "sports"

    def test_general(self):
        assert Topic.GENERAL.value == "general"


class TestCrisisTypeEnum:

    def test_has_three_values(self):
        assert len(CrisisType) == 3

    def test_election(self):
        assert CrisisType.ELECTION.value == "election"

    def test_natural_disaster(self):
        assert CrisisType.NATURAL_DISASTER.value == "natural_disaster"

    def test_civil_unrest(self):
        assert CrisisType.CIVIL_UNREST.value == "civil_unrest"


class TestModeratorRoleEnum:

    def test_has_three_values(self):
        assert len(ModeratorRole) == 3

    def test_senior(self):
        assert ModeratorRole.SENIOR.value == "senior"

    def test_junior(self):
        assert ModeratorRole.JUNIOR.value == "junior"

    def test_specialist(self):
        assert ModeratorRole.SPECIALIST.value == "specialist"


class TestContentItemDataclass:

    def test_defaults(self):
        item = ContentItem(id="test_1", title="Test", description="A test item")
        assert item.content_type == ContentType.TEXT
        assert item.author_type == AuthorType.ANONYMOUS
        assert item.author_name == "Anonymous User"
        assert item.author_followers == 0
        assert item.topic == Topic.GENERAL
        assert item.report_reason == ReportReason.SPAM
        assert item.report_count == 1
        assert item.toxicity_score == 0.5
        assert item.actual_harm_level == HarmLevel.LOW
        assert item.political_leaning == PoliticalLeaning.NONPOLITICAL
        assert item.is_satire is False
        assert item.has_news_value is False
        assert item.context_needed is False
        assert item.cultural_sensitivity is False
        assert item.is_coordinated is False
        assert item.is_appeal is False
        assert item.original_decision_id == ""
        assert item.arrival_hour == 0
        assert item.status == ModerationAction.PENDING
        assert item.decision_reason == ""
        assert item.reviewed_by == ""
        assert item.review_hour == -1
        assert item.viral_potential == 0.0
        assert item.engagement_rate == 0.0


class TestModeratorDataclass:

    def test_defaults(self):
        mod = Moderator(id="mod_1", name="Test Mod")
        assert mod.role == ModeratorRole.JUNIOR
        assert mod.specialization == ""
        assert mod.fatigue == 0.0
        assert mod.accuracy_rate == 0.85
        assert mod.items_reviewed == 0
        assert mod.errors_made == 0
        assert mod.on_duty is True
        assert mod.is_resting is False
        assert mod.hours_worked == 0.0
        assert mod.breaks_taken == 0
        assert mod.current_item == ""


class TestStakeholderPressureDataclass:

    def test_defaults(self):
        sp = StakeholderPressure()
        assert sp.advertiser_satisfaction == 70.0
        assert sp.political_pressure_left == 0.0
        assert sp.political_pressure_right == 0.0
        assert sp.media_scrutiny == 20.0
        assert sp.user_petitions == 0
        assert sp.government_requests == 0
        assert sp.government_requests_complied == 0
        assert sp.advertiser_demands == []
        assert sp.political_demands == []


class TestPlatformMetricsDataclass:

    def test_defaults(self):
        pm = PlatformMetrics()
        assert pm.throughput == 0
        assert pm.avg_response_time == 0.0
        assert pm.user_satisfaction == 70.0
        assert pm.content_removed_count == 0
        assert pm.content_approved_count == 0
        assert pm.content_labeled_count == 0
        assert pm.appeals_received == 0
        assert pm.appeals_granted == 0
        assert pm.appeals_denied == 0
        assert pm.false_positive_visible == 0
        assert pm.platform_reputation == 70.0
        assert pm.revenue_impact == 0.0


class TestTransparencyStateDataclass:

    def test_defaults(self):
        ts = TransparencyState()
        assert ts.report_published is False
        assert ts.report_honest is True
        assert ts.stats_suppressed == []
        assert ts.policies_public is True
        assert ts.removal_reasons_given == 0
        assert ts.removal_reasons_withheld == 0


class TestAutoModConfigDataclass:

    def test_defaults(self):
        amc = AutoModConfig()
        assert amc.toxicity_threshold == 0.8
        assert amc.auto_approve_verified is False
        assert amc.auto_approve_politicians is False
        assert amc.batch_mode_enabled is False
        assert amc.context_review_enabled is True


class TestAppealCaseDataclass:

    def test_defaults(self):
        ac = AppealCase(
            id="appeal_1",
            original_content_id="content_1",
            appeal_reason="Test appeal",
        )
        assert ac.new_context == ""
        assert ac.has_merit is False
        assert ac.status == "pending"
        assert ac.review_hour == -1
