"""Normalization utilities: text cleaning, URL canonicalization, ID generation, date parsing."""

import hashlib
import re
from urllib.parse import urlparse, urlencode, parse_qs

from oppwatch.models import Opportunity

_TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                    "ref", "fbclid", "gclid", "source"}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(s: str, max_len: int = 500) -> str:
    """Strip HTML tags, collapse whitespace, trim to max_len."""
    text = _HTML_TAG_RE.sub(" ", s)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text[:max_len]


def canonical_url(url: str) -> str:
    """Lowercase scheme+host, remove fragment, remove tracking params, remove trailing slash, sort params."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path
    params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in params.items() if k not in _TRACKING_PARAMS
                and not k.startswith("utm_")}
    query = urlencode(sorted(filtered.items()), doseq=True) if filtered else ""
    result = f"{scheme}://{host}{path}"
    if query:
        result += f"?{query}"
    return result


def make_id(url: str, title: str, source: str) -> str:
    """sha1 hex of canonical_url(url) if url non-empty, else of lowercase(title)+'|'+source."""
    if url:
        text = canonical_url(url)
    else:
        text = title.lower() + "|" + source
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def to_date(value: object) -> str | None:
    """Convert epoch seconds, ISO strings, or None into 'YYYY-MM-DD'. Return None if unparseable."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            from datetime import datetime, timezone
            return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%d")
        except (OSError, ValueError, OverflowError):
            return None
    s = str(value).strip()
    if not s:
        return None
    # Try digit string (epoch seconds)
    if s.replace(".", "", 1).isdigit():
        try:
            from datetime import datetime, timezone
            return datetime.fromtimestamp(float(s), tz=timezone.utc).strftime("%Y-%m-%d")
        except (OSError, ValueError, OverflowError):
            return None
    # Try YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if match:
        date_str = match.group(1)
        # Validate it's a real date
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            return None
    return None


def make_opportunity(raw: dict, kind: str, source: str) -> Opportunity | None:
    """Build an Opportunity from a raw dict. Return None if title or url is empty."""
    title = clean_text(str(raw.get("title", "")))
    url = str(raw.get("url", "")).strip()
    if not title or not url:
        return None
    opp_id = make_id(url, title, source)
    return Opportunity(
        id=opp_id,
        kind=kind,
        title=title,
        url=url,
        source=source,
        org=clean_text(str(raw.get("org", ""))),
        location=clean_text(str(raw.get("location", ""))),
        deadline=to_date(raw.get("deadline")),
        posted_at=to_date(raw.get("posted_at")),
        description=clean_text(str(raw.get("description", ""))),
    )
