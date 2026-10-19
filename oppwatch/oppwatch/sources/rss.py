"""RSS source plugin: fetch and parse RSS/Atom feeds."""

import logging

import feedparser

from oppwatch import net
from oppwatch.models import Opportunity
from oppwatch.normalize import make_opportunity

logger = logging.getLogger(__name__)


def fetch(cfg: dict) -> list[Opportunity]:
    """Fetch an RSS feed and return normalized Opportunity objects."""
    url = cfg["url"]
    kind = cfg["kind"]
    source = cfg["name"]
    resp = net.get(url)
    feed = feedparser.parse(resp.content)
    results: list[Opportunity] = []
    for entry in feed.entries:
        raw = {
            "title": getattr(entry, "title", ""),
            "url": getattr(entry, "link", ""),
            "description": entry.get("summary", ""),
            "posted_at": entry.get("published", None),
        }
        opp = make_opportunity(raw, kind, source)
        if opp is not None:
            results.append(opp)
    logger.info("RSS source '%s': fetched %d items", source, len(results))
    return results
