"""Opportunity scoring and filtering based on user configuration."""

from datetime import date
import re

from oppwatch.models import Opportunity


def _matches_word(keyword: str, text: str) -> bool:
    """Return True if keyword matches as a whole word in text (case-insensitive)."""
    if not keyword or not text:
        return False
    return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE))


def score_item(item: Opportunity, f: dict) -> int:
    """Calculate score: +3 title kw, +1 desc kw, +2 preferred loc, -5 exclude kw."""
    score = 0
    title = item.title or ""
    desc = item.description or ""
    location = item.location or ""

    for kw in f.get("include_keywords", []):
        if _matches_word(kw, title):
            score += 3
        if _matches_word(kw, desc):
            score += 1

    pref_locations = f.get("preferred_locations", [])
    has_pref_loc = any(_matches_word(loc, location) or _matches_word(loc, title) for loc in pref_locations)
    if has_pref_loc:
        score += 2

    for kw in f.get("exclude_keywords", []):
        if _matches_word(kw, title) or _matches_word(kw, desc):
            score -= 5

    return score


def apply_filters(items: list[Opportunity], f: dict, today: str) -> list[Opportunity]:
    """Score items and drop those failing kind, score, deadline, or age criteria."""
    allowed_kinds = set(f.get("kinds", ["hackathon", "internship"]))
    min_score = f.get("min_score", 0)
    drop_past = f.get("drop_past_deadlines", True)
    max_age = f.get("max_age_days", 45)
    today_date = date.fromisoformat(today)

    survivors: list[Opportunity] = []
    for item in items:
        if item.kind not in allowed_kinds:
            continue

        item.score = score_item(item, f)
        if item.score < min_score:
            continue

        if drop_past and item.deadline is not None:
            if item.deadline < today:
                continue

        if item.posted_at is not None:
            try:
                posted_date = date.fromisoformat(item.posted_at)
                if (today_date - posted_date).days > max_age:
                    continue
            except ValueError:
                pass

        survivors.append(item)

    survivors.sort(key=lambda opp: opp.score, reverse=True)
    return survivors
