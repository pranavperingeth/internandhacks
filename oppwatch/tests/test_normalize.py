"""Tests for normalize.py (Phase 2)."""

from oppwatch.normalize import canonical_url, make_id, to_date, clean_text, make_opportunity


def test_canonical_url_removes_tracking_and_fragment():
    """canonical_url removes utm_*, fragment, lowercases host, keeps other params sorted."""
    result = canonical_url("https://Example.com/a/?utm_source=x&b=2#frag")
    assert result == "https://example.com/a?b=2"


def test_make_id_stable_across_tracking_params():
    """make_id gives the same value for URLs differing only by utm_campaign."""
    id1 = make_id("https://example.com/job?utm_campaign=a", "T", "s")
    id2 = make_id("https://example.com/job?utm_campaign=b", "T", "s")
    assert id1 == id2


def test_to_date_epoch_seconds():
    """to_date(1767225600) returns a YYYY-MM-DD string."""
    result = to_date(1767225600)
    assert result is not None
    assert len(result) == 10
    assert result[4] == "-" and result[7] == "-"


def test_to_date_iso_string():
    """to_date with ISO datetime returns just the date part."""
    assert to_date("2026-11-05T10:00:00Z") == "2026-11-05"


def test_to_date_range_string():
    """to_date parses English month ranges and returns deadline YYYY-MM-DD."""
    assert to_date("Oct 30 - Dec 04, 2026") == "2026-12-04"
    assert to_date("Nov 02, 2026") == "2026-11-02"
    assert to_date("Dec 18 - 21, 2026") == "2026-12-21"


def test_to_date_garbage():
    """to_date returns None for unparseable input."""
    assert to_date("garbage") is None


def test_to_date_none():
    """to_date returns None for None input."""
    assert to_date(None) is None


def test_clean_text_strips_html():
    """clean_text strips tags and collapses whitespace."""
    assert clean_text("<p>Hello   <b>world</b></p>") == "Hello world"


def test_clean_text_trims_length():
    """clean_text trims to max_len."""
    result = clean_text("a" * 1000, max_len=50)
    assert len(result) == 50


def test_make_opportunity_empty_title_returns_none():
    """make_opportunity returns None when title is empty."""
    result = make_opportunity({"title": "", "url": "http://x"}, "hackathon", "s")
    assert result is None


def test_make_opportunity_empty_url_returns_none():
    """make_opportunity returns None when url is empty."""
    result = make_opportunity({"title": "Test", "url": ""}, "hackathon", "s")
    assert result is None


def test_make_opportunity_valid():
    """make_opportunity returns a valid Opportunity with cleaned fields."""
    raw = {
        "title": "<b>Software Intern</b>",
        "url": "https://example.com/job",
        "org": "Acme",
        "location": "Bengaluru",
        "deadline": "2026-12-01",
        "posted_at": "2026-10-01",
        "description": "<p>Great opportunity</p>",
    }
    opp = make_opportunity(raw, "internship", "test_source")
    assert opp is not None
    assert opp.title == "Software Intern"
    assert opp.kind == "internship"
    assert opp.source == "test_source"
    assert opp.deadline == "2026-12-01"
    assert opp.description == "Great opportunity"
