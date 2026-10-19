from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Opportunity:
    """A single hackathon or internship listing."""

    id: str                       # stable hash, set by normalize.make_id
    kind: str                     # "hackathon" | "internship" | "other"
    title: str
    url: str
    source: str                   # source name from sources.yaml
    org: str = ""                 # company or organizer, may be empty
    location: str = ""            # free text, may be empty
    deadline: Optional[str] = None    # "YYYY-MM-DD" or None
    posted_at: Optional[str] = None   # "YYYY-MM-DD" or None
    description: str = ""         # plain text, max 500 chars
    score: int = 0                # filled by filters.py
    summary: str = ""             # filled by llm.py (Phase 11), else empty

    def to_dict(self) -> dict:
        """Return the dataclass as a plain dict."""
        return asdict(self)
