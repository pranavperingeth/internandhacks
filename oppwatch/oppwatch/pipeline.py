"""Orchestration pipeline: fetch, deduplicate, filter, store, and notify."""

from datetime import date
import logging
import os

from dotenv import load_dotenv

from oppwatch import db
from oppwatch.config import get_env, load_filters, load_sources
from oppwatch.digest import build_digest
from oppwatch.filters import apply_filters
from oppwatch.models import Opportunity
from oppwatch.notifiers import NOTIFIERS
from oppwatch.sources import SOURCE_TYPES

logger = logging.getLogger(__name__)


def run(dry_run: bool = False, only: str | None = None) -> dict:
    """Run full pipeline: fetch sources, filter, update DB, and send digest."""
    load_dotenv()
    sources = load_sources()
    filters = load_filters()
    today = date.today().isoformat()
    db_path = get_env("DB_PATH", "data/seen.db")
    notifier_name = get_env("NOTIFIER", "console")

    if only:
        sources = [s for s in sources if s.get("name") == only]

    sources_ok = 0
    sources_failed = 0
    all_items: list[Opportunity] = []

    for src in sources:
        name = src.get("name", "unnamed")
        src_type = src.get("type", "")
        fetcher = SOURCE_TYPES.get(src_type)
        if not fetcher:
            logger.error("source %s failed: unknown type '%s'", name, src_type)
            sources_failed += 1
            continue
        try:
            items = fetcher(src)
            all_items.extend(items)
            sources_ok += 1
        except Exception as exc:
            logger.error("source %s failed: %s", name, exc)
            sources_failed += 1

    fetched_count = len(all_items)

    # Deduplicate by id within this run (keep first)
    seen_ids: set[str] = set()
    unique_items: list[Opportunity] = []
    for item in all_items:
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            unique_items.append(item)

    kept = apply_filters(unique_items, filters, today)

    # Optional local LLM enrichment (Phase 11)
    ollama_model = get_env("OLLAMA_MODEL")
    if ollama_model:
        try:
            from oppwatch.llm import enrich
            kept = enrich(kept)
        except Exception as exc:
            logger.warning("LLM enrichment failed: %s", exc)

    conn = db.connect(db_path)
    new_items = db.upsert_new(conn, kept, today)
    new_count = len(new_items)
    pending = db.pending_notifications(conn)

    max_digest = filters.get("max_items_per_kind_in_digest", 25)
    text = build_digest(pending, max_digest, today)

    if dry_run:
        if text:
            print(text)
        logger.info("Dry run complete")
        conn.close()
        return {
            "sources_ok": sources_ok,
            "sources_failed": sources_failed,
            "fetched": fetched_count,
            "kept": len(kept),
            "new": new_count,
            "sent": False,
        }

    if not text:
        logger.info("nothing new")
        conn.close()
        return {
            "sources_ok": sources_ok,
            "sources_failed": sources_failed,
            "fetched": fetched_count,
            "kept": len(kept),
            "new": new_count,
            "sent": False,
        }

    notifier_fn = NOTIFIERS.get(notifier_name, NOTIFIERS["console"])
    sent_ok = notifier_fn(text)
    if sent_ok:
        db.mark_notified(conn, [i.id for i in pending])

    conn.close()
    return {
        "sources_ok": sources_ok,
        "sources_failed": sources_failed,
        "fetched": fetched_count,
        "kept": len(kept),
        "new": new_count,
        "sent": sent_ok,
    }
