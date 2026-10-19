"""Local LLM enrichment for relevance validation and summary generation using Ollama."""

import json
import logging
import re
import requests

from oppwatch.config import get_env
from oppwatch.models import Opportunity

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You help a CS student find hackathons and internships.
Read the listing and answer with ONLY a JSON object, no other text.

Listing:
Title: {title}
Organization: {org}
Location: {location}
Text: {description}

Return exactly:
{{"relevant": true or false, "summary": "max 20 words", "deadline": "YYYY-MM-DD" or null}}

relevant = true only if it is a software, data, AI, or engineering hackathon or internship open to students in India or remote.
Use deadline only if a date is clearly stated in the text, otherwise null."""

DEADLINE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _call_ollama(model: str, prompt: str) -> dict | None:
    """Send generation request to local Ollama API and return parsed JSON."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }
    resp = requests.post(url, json=payload, timeout=60)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if isinstance(data, dict) and "response" in data:
        resp_content = data["response"]
        return json.loads(resp_content) if isinstance(resp_content, str) else resp_content
    return data if isinstance(data, dict) else None


def enrich(items: list[Opportunity], max_items: int = 40) -> list[Opportunity]:
    """For the top `max_items` by score, ask the local model for relevance + summary."""
    model = get_env("OLLAMA_MODEL")
    if not model or not items:
        return items

    enriched_items: list[Opportunity] = []
    to_process = items[:max_items]
    remainder = items[max_items:]

    for item in to_process:
        desc_truncated = (item.description or "")[:400]
        prompt = PROMPT_TEMPLATE.format(
            title=item.title,
            org=item.org,
            location=item.location,
            description=desc_truncated,
        )
        try:
            parsed = _call_ollama(model, prompt)
            if not parsed or not isinstance(parsed, dict):
                enriched_items.append(item)
                continue

            relevant = parsed.get("relevant")
            summary = parsed.get("summary")
            deadline_val = parsed.get("deadline")

            if not isinstance(relevant, bool):
                enriched_items.append(item)
                continue

            if not isinstance(summary, str) or len(summary) > 120:
                enriched_items.append(item)
                continue

            if deadline_val is not None:
                if not (isinstance(deadline_val, str) and DEADLINE_PATTERN.match(deadline_val)):
                    enriched_items.append(item)
                    continue

            if not relevant:
                continue

            item.summary = summary
            if deadline_val and not item.deadline:
                item.deadline = deadline_val
            enriched_items.append(item)
        except Exception as exc:
            logger.warning("LLM enrichment error for item %s: %s", item.id, exc)
            enriched_items.append(item)

    return enriched_items + remainder
