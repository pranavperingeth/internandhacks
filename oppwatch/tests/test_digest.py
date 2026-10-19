"""Tests for digest builder and message splitting (Phase 6)."""

from oppwatch.digest import build_digest, split_message
from oppwatch.models import Opportunity


def test_build_digest_empty_list() -> None:
    """Empty list returns empty string."""
    assert build_digest([], 25, "2026-10-26") == ""


def test_build_digest_grouping_order() -> None:
    """Grouping order: hackathons first, then internships, then other."""
    items = [
        Opportunity(id="1", kind="internship", title="Job 1", url="http://job.com", source="s"),
        Opportunity(id="2", kind="hackathon", title="Hack 1", url="http://hack.com", source="s"),
        Opportunity(id="3", kind="other", title="Other 1", url="http://other.com", source="s"),
    ]
    digest = build_digest(items, 25, "2026-10-26")
    pos_hack = digest.find("HACKATHONS (1)")
    pos_intern = digest.find("INTERNSHIPS (1)")
    pos_other = digest.find("OTHER (1)")
    assert pos_hack != -1
    assert pos_intern != -1
    assert pos_other != -1
    assert pos_hack < pos_intern < pos_other


def test_none_deadlines_come_last() -> None:
    """Inside each group, None deadlines come last."""
    items = [
        Opportunity(id="1", kind="hackathon", title="No Deadline", url="http://a.com", source="s", deadline=None),
        Opportunity(id="2", kind="hackathon", title="Early Deadline", url="http://b.com", source="s", deadline="2026-11-01"),
        Opportunity(id="3", kind="hackathon", title="Late Deadline", url="http://c.com", source="s", deadline="2026-11-15"),
    ]
    digest = build_digest(items, 25, "2026-10-26")
    pos_early = digest.find("Early Deadline")
    pos_late = digest.find("Late Deadline")
    pos_none = digest.find("No Deadline")
    assert pos_early < pos_late < pos_none


def test_truncation_line_appears() -> None:
    """Truncation line '+N more' appears with 30 items and max_per_kind=25."""
    items = [
        Opportunity(id=f"id{i}", kind="internship", title=f"Internship {i}", url=f"http://job{i}.com", source="s")
        for i in range(30)
    ]
    digest = build_digest(items, 25, "2026-10-26")
    assert "+5 more" in digest
    assert "INTERNSHIPS (30)" in digest
    assert "Internship 24" in digest
    assert "Internship 25" not in digest


def test_summary_inclusion() -> None:
    """Opportunity summary is included as an indented third line when present."""
    item = Opportunity(
        id="1",
        kind="hackathon",
        title="Hack AI",
        url="http://hack.com",
        source="s",
        summary="Build generative AI solutions for climate.",
    )
    digest = build_digest([item], 25, "2026-10-26")
    assert "   Build generative AI solutions for climate." in digest


def test_split_message_respects_limit() -> None:
    """split_message chunks are all <= limit and preserve content."""
    lines = [f"Line {i}: " + ("x" * 50) for i in range(100)]
    text = "\n".join(lines)
    chunks = split_message(text, limit=500)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 500
    assert "\n".join(chunks) == text
