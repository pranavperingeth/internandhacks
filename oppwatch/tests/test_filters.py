"""Tests for filtering and scoring (Phase 5)."""

from datetime import date, timedelta
from oppwatch.filters import score_item, apply_filters, _matches_word
from oppwatch.models import Opportunity

SAMPLE_FILTERS = {
    "kinds": ["hackathon", "internship"],
    "include_keywords": ["software", "engineer", "intern", "ai"],
    "exclude_keywords": ["marketing", "sales"],
    "preferred_locations": ["bengaluru", "remote"],
    "min_score": 2,
    "max_age_days": 45,
    "drop_past_deadlines": True,
}


def test_preferred_location_scores_higher() -> None:
    """'Software Engineer Intern' in Bengaluru scores higher than in an unlisted location."""
    opp_bengaluru = Opportunity(
        id="1",
        kind="internship",
        title="Software Engineer Intern",
        url="https://a.com",
        source="src",
        location="Bengaluru",
    )
    opp_other = Opportunity(
        id="2",
        kind="internship",
        title="Software Engineer Intern",
        url="https://b.com",
        source="src",
        location="Nowhere",
    )
    score1 = score_item(opp_bengaluru, SAMPLE_FILTERS)
    score2 = score_item(opp_other, SAMPLE_FILTERS)
    assert score1 > score2
    assert score1 - score2 == 2


def test_exclude_keyword_drops_item() -> None:
    """Title containing 'Marketing Intern' is dropped due to negative score and exclude keyword."""
    opp = Opportunity(
        id="1",
        kind="internship",
        title="Marketing Intern",
        url="https://a.com",
        source="src",
    )
    survivors = apply_filters([opp], SAMPLE_FILTERS, "2026-10-26")
    assert len(survivors) == 0


def test_deadlines_filtering() -> None:
    """A deadline of yesterday is dropped; deadline of tomorrow is kept; None deadline is kept."""
    today = date(2026, 10, 26)
    yesterday = (today - timedelta(days=1)).isoformat()
    tomorrow = (today + timedelta(days=1)).isoformat()
    today_str = today.isoformat()

    opp_past = Opportunity(
        id="1", kind="hackathon", title="Software Hackathon", url="https://a.com", source="src", deadline=yesterday
    )
    opp_future = Opportunity(
        id="2", kind="hackathon", title="Software Hackathon", url="https://b.com", source="src", deadline=tomorrow
    )
    opp_none = Opportunity(
        id="3", kind="hackathon", title="Software Hackathon", url="https://c.com", source="src", deadline=None
    )

    survivors = apply_filters([opp_past, opp_future, opp_none], SAMPLE_FILTERS, today_str)
    survivor_ids = [item.id for item in survivors]
    assert "1" not in survivor_ids
    assert "2" in survivor_ids
    assert "3" in survivor_ids


def test_word_boundary_matching() -> None:
    """'ai' does not match inside 'maintain'."""
    assert not _matches_word("ai", "Please maintain this code")
    assert _matches_word("ai", "Exciting AI challenge")


def test_result_order_score_descending() -> None:
    """Result order is score descending."""
    opp_low = Opportunity(
        id="low", kind="internship", title="Software Intern", url="https://a.com", source="src"
    )
    opp_high = Opportunity(
        id="high",
        kind="internship",
        title="Software Engineer Intern AI",
        url="https://b.com",
        source="src",
        location="Bengaluru",
    )
    today_str = "2026-10-26"
    survivors = apply_filters([opp_low, opp_high], SAMPLE_FILTERS, today_str)
    assert len(survivors) == 2
    assert survivors[0].id == "high"
    assert survivors[1].id == "low"
    assert survivors[0].score >= survivors[1].score
