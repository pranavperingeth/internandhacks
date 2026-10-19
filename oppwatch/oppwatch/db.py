"""SQLite database operations for tracking seen and notified opportunities."""

import os
from pathlib import Path
import sqlite3

from oppwatch.models import Opportunity

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    org TEXT,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    deadline TEXT,
    score INTEGER DEFAULT 0,
    first_seen TEXT NOT NULL,   -- YYYY-MM-DD
    last_seen TEXT NOT NULL,    -- YYYY-MM-DD
    notified INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: str) -> sqlite3.Connection:
    """Create parent dir if needed, open the DB, create the table, return the connection."""
    if path != ":memory:":
        parent = Path(path).parent
        if str(parent) != "" and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    with conn:
        conn.execute(SCHEMA)
    return conn


def upsert_new(conn: sqlite3.Connection, items: list[Opportunity], today: str) -> list[Opportunity]:
    """For each item: if id not in DB, INSERT; if exists, only UPDATE last_seen. Return new items."""
    new_items: list[Opportunity] = []
    with conn:
        cursor = conn.cursor()
        for item in items:
            cursor.execute("SELECT id FROM seen WHERE id = ?", (item.id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    """
                    INSERT INTO seen (id, kind, title, org, url, source, deadline, score, first_seen, last_seen, notified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        item.id,
                        item.kind,
                        item.title,
                        item.org,
                        item.url,
                        item.source,
                        item.deadline,
                        item.score,
                        today,
                        today,
                    ),
                )
                new_items.append(item)
            else:
                cursor.execute(
                    "UPDATE seen SET last_seen = ? WHERE id = ?",
                    (today, item.id),
                )
    return new_items


def pending_notifications(conn: sqlite3.Connection) -> list[Opportunity]:
    """Return items where notified = 0 as Opportunity objects (description empty is fine)."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, kind, title, org, url, source, deadline, score
        FROM seen
        WHERE notified = 0
        """
    )
    rows = cursor.fetchall()
    return [
        Opportunity(
            id=row[0],
            kind=row[1],
            title=row[2],
            org=row[3] or "",
            url=row[4],
            source=row[5],
            deadline=row[6],
            score=row[7] or 0,
        )
        for row in rows
    ]


def mark_notified(conn: sqlite3.Connection, ids: list[str]) -> None:
    """Set notified = 1 for the given ids and commit."""
    with conn:
        cursor = conn.cursor()
        cursor.executemany("UPDATE seen SET notified = 1 WHERE id = ?", [(item_id,) for item_id in ids])
