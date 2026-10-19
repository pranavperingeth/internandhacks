"""Tests for database operations (Phase 4)."""

from pathlib import Path
import sqlite3

from oppwatch import db
from oppwatch.models import Opportunity


def test_upsert_new_deduplicates(tmp_path: Path) -> None:
    """First upsert_new with 2 items returns 2; second call with same items returns 0."""
    db_file = str(tmp_path / "test.db")
    conn = db.connect(db_file)

    items = [
        Opportunity(id="id1", kind="hackathon", title="Hack 1", url="https://a.com", source="src"),
        Opportunity(id="id2", kind="internship", title="Intern 1", url="https://b.com", source="src"),
    ]

    new_items_1 = db.upsert_new(conn, items, "2026-10-26")
    assert len(new_items_1) == 2

    new_items_2 = db.upsert_new(conn, items, "2026-10-27")
    assert len(new_items_2) == 0
    conn.close()


def test_pending_notifications_and_mark_notified(tmp_path: Path) -> None:
    """pending_notifications returns 2 after first call; after mark_notified for both returns 0."""
    db_file = str(tmp_path / "test.db")
    conn = db.connect(db_file)

    items = [
        Opportunity(id="id1", kind="hackathon", title="Hack 1", url="https://a.com", source="src"),
        Opportunity(id="id2", kind="internship", title="Intern 1", url="https://b.com", source="src"),
    ]

    db.upsert_new(conn, items, "2026-10-26")
    pending = db.pending_notifications(conn)
    assert len(pending) == 2

    db.mark_notified(conn, [item.id for item in pending])
    pending_after = db.pending_notifications(conn)
    assert len(pending_after) == 0
    conn.close()


def test_second_run_updates_last_seen_preserves_first_seen(tmp_path: Path) -> None:
    """A second run keeps first_seen unchanged but updates last_seen."""
    db_file = str(tmp_path / "test.db")
    conn = db.connect(db_file)

    items = [
        Opportunity(id="id1", kind="hackathon", title="Hack 1", url="https://a.com", source="src"),
    ]

    db.upsert_new(conn, items, "2026-10-26")
    cursor = conn.cursor()
    cursor.execute("SELECT first_seen, last_seen FROM seen WHERE id = 'id1'")
    row1 = cursor.fetchone()
    assert row1 == ("2026-10-26", "2026-10-26")

    db.upsert_new(conn, items, "2026-11-02")
    cursor.execute("SELECT first_seen, last_seen FROM seen WHERE id = 'id1'")
    row2 = cursor.fetchone()
    assert row2 == ("2026-10-26", "2026-11-02")
    conn.close()
