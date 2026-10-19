"""Tests for pipeline execution and notifier delivery (Phase 7 & 8)."""

from pathlib import Path
import pytest

from oppwatch import pipeline
from oppwatch.models import Opportunity
from oppwatch.notifiers import telegram


def _make_sample_items() -> list[Opportunity]:
    """Create sample opportunities for testing."""
    return [
        Opportunity(id="id1", kind="hackathon", title="AI Hackathon", url="https://a.com", source="src1", score=10),
        Opportunity(id="id2", kind="internship", title="Software Intern", url="https://b.com", source="src1", score=10),
        Opportunity(id="id3", kind="internship", title="Developer Intern", url="https://c.com", source="src1", score=10),
    ]


def test_pipeline_sources_ok_and_failure(monkeypatch, tmp_path: Path) -> None:
    """The run completes with sources_ok == 1 and sources_failed == 1."""
    db_file = str(tmp_path / "test_pipeline.db")
    monkeypatch.setenv("DB_PATH", db_file)
    monkeypatch.setenv("NOTIFIER", "console")

    fake_sources = [
        {"name": "good", "type": "rss", "kind": "hackathon", "enabled": True, "url": "http://good"},
        {"name": "failing", "type": "bad_type", "kind": "hackathon", "enabled": True, "url": "http://bad"},
    ]
    monkeypatch.setattr("oppwatch.pipeline.load_sources", lambda: fake_sources)
    monkeypatch.setattr("oppwatch.pipeline.SOURCE_TYPES", {"rss": lambda cfg: _make_sample_items()})

    stats = pipeline.run(dry_run=False)
    assert stats["sources_ok"] == 1
    assert stats["sources_failed"] == 1
    assert stats["new"] == 3
    assert stats["sent"] is True

    # A second run right after sends nothing new (new == 0)
    stats2 = pipeline.run(dry_run=False)
    assert stats2["new"] == 0
    assert stats2["sent"] is False


def test_pipeline_dry_run_does_not_mark_notified(monkeypatch, tmp_path: Path) -> None:
    """With dry_run=True items are saved in DB but NOT marked notified."""
    db_file = str(tmp_path / "test_dry_run.db")
    monkeypatch.setenv("DB_PATH", db_file)
    monkeypatch.setenv("NOTIFIER", "console")

    fake_sources = [
        {"name": "good", "type": "rss", "kind": "hackathon", "enabled": True, "url": "http://good"},
    ]
    monkeypatch.setattr("oppwatch.pipeline.load_sources", lambda: fake_sources)
    monkeypatch.setattr("oppwatch.pipeline.SOURCE_TYPES", {"rss": lambda cfg: _make_sample_items()})

    stats = pipeline.run(dry_run=True)
    assert stats["new"] == 3
    assert stats["sent"] is False

    from oppwatch import db
    conn = db.connect(db_file)
    pending = db.pending_notifications(conn)
    assert len(pending) == 3
    conn.close()


def test_pipeline_failed_notifier_keeps_pending(monkeypatch, tmp_path: Path) -> None:
    """If notifier returns False, items stay pending and are sent next run."""
    db_file = str(tmp_path / "test_notifier_fail.db")
    monkeypatch.setenv("DB_PATH", db_file)

    fake_sources = [
        {"name": "good", "type": "rss", "kind": "hackathon", "enabled": True, "url": "http://good"},
    ]
    monkeypatch.setattr("oppwatch.pipeline.load_sources", lambda: fake_sources)
    monkeypatch.setattr("oppwatch.pipeline.SOURCE_TYPES", {"rss": lambda cfg: _make_sample_items()})

    # First run with failing notifier
    monkeypatch.setattr("oppwatch.pipeline.NOTIFIERS", {"console": lambda text: False})
    stats1 = pipeline.run(dry_run=False)
    assert stats1["sent"] is False

    # Second run with succeeding notifier sends the pending items
    monkeypatch.setattr("oppwatch.pipeline.NOTIFIERS", {"console": lambda text: True})
    stats2 = pipeline.run(dry_run=False)
    assert stats2["new"] == 0
    assert stats2["sent"] is True


def test_telegram_send_success_and_missing_token(monkeypatch) -> None:
    """telegram.send returns True for 200 response and False when token is empty."""
    class FakeResp:
        status_code = 200

    monkeypatch.setattr("requests.post", lambda url, data=None, timeout=None: FakeResp())
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    assert telegram.send("Test message") is True

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    assert telegram.send("Test message") is False
