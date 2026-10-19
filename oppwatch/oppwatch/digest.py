"""Plain-text digest generator and message chunking for notifications."""

from oppwatch.models import Opportunity

KIND_ORDER = ["hackathon", "internship", "other"]
KIND_HEADERS = {
    "hackathon": "HACKATHONS",
    "internship": "INTERNSHIPS",
    "other": "OTHER",
}


def _format_opportunity(idx: int, item: Opportunity) -> str:
    """Format a single Opportunity into plain text with optional summary."""
    title_part = f"{item.title} at {item.org}" if item.org and item.org.lower() not in item.title.lower() else item.title
    parts = [f"{idx}. {title_part}"]
    if item.location:
        parts.append(item.location)
    parts.append(f"deadline {item.deadline}" if item.deadline else "deadline: n/a")
    line1 = " | ".join(parts)
    lines = [line1, f"   {item.url}"]
    if item.summary:
        lines.append(f"   {item.summary}")
    return "\n".join(lines)


def build_digest(items: list[Opportunity], max_per_kind: int, today: str) -> str:
    """Plain text (no markdown symbols that need escaping). Return '' if items is empty."""
    if not items:
        return ""

    sections: list[str] = [f"Weekly Opportunities ({today})\nNew this week: {len(items)}"]

    # Group items by kind
    grouped: dict[str, list[Opportunity]] = {}
    for item in items:
        k = item.kind if item.kind in KIND_HEADERS else "other"
        grouped.setdefault(k, []).append(item)

    for kind in KIND_ORDER:
        kind_items = grouped.get(kind, [])
        if not kind_items:
            continue

        # Sort: deadline ascending, None last
        kind_items.sort(key=lambda x: (x.deadline is None, x.deadline or ""))

        header_title = KIND_HEADERS.get(kind, kind.upper())
        section_lines = [f"{header_title} ({len(kind_items)})"]

        displayed = kind_items[:max_per_kind]
        for idx, item in enumerate(displayed, start=1):
            section_lines.append(_format_opportunity(idx, item))

        remaining = len(kind_items) - len(displayed)
        if remaining > 0:
            section_lines.append(f"+{remaining} more")

        sections.append("\n".join(section_lines))

    return "\n\n".join(sections)


def split_message(text: str, limit: int = 3800) -> list[str]:
    """Split on blank lines or line breaks so each chunk is <= limit chars. Never cut inside a line."""
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    lines = text.split("\n")
    chunks: list[str] = []
    current_lines: list[str] = []
    current_len = 0

    for line in lines:
        line_len = len(line) + (1 if current_lines else 0)
        if current_len + line_len <= limit:
            current_lines.append(line)
            current_len += line_len
        else:
            if current_lines:
                chunks.append("\n".join(current_lines))
            current_lines = [line]
            current_len = len(line)

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks
