"""Tests for local LLM enrichment (Phase 11)."""

import json
import pytest
import requests

from oppwatch.llm import enrich
from oppwatch.models import Opportunity


class FakeLLMResponse:
    """Mock requests response returning JSON payload."""

    def __init__(self, data: dict, status_code: int = 200) -> None:
        """Initialize mock response."""
        self._data = data
        self.status_code = status_code

    def json(self) -> dict:
        """Return the pre-configured dictionary."""
        return self._data


def test_valid_json_sets_summary_and_deadline(monkeypatch) -> None:
    """Valid JSON sets summary and fills empty deadline."""
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    response_data = {
        "response": json.dumps({
            "relevant": True,
            "summary": "Great machine learning internship",
            "deadline": "2026-12-15",
        })
    }
    monkeypatch.setattr("requests.post", lambda url, json=None, timeout=None: FakeLLMResponse(response_data))

    item = Opportunity(id="1", kind="internship", title="ML Intern", url="http://x", source="s")
    result = enrich([item])
    assert len(result) == 1
    assert result[0].summary == "Great machine learning internship"
    assert result[0].deadline == "2026-12-15"


def test_invalid_json_leaves_item_unchanged(monkeypatch) -> None:
    """Invalid JSON leaves the item unchanged without errors."""
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    response_data = {"response": "This is plain text, not valid json"}
    monkeypatch.setattr("requests.post", lambda url, json=None, timeout=None: FakeLLMResponse(response_data))

    item = Opportunity(id="1", kind="internship", title="ML Intern", url="http://x", source="s")
    result = enrich([item])
    assert len(result) == 1
    assert result[0].summary == ""


def test_relevant_false_drops_item(monkeypatch) -> None:
    """relevant: false drops the item from the list."""
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    response_data = {
        "response": json.dumps({
            "relevant": False,
            "summary": "Not a student job",
            "deadline": None,
        })
    }
    monkeypatch.setattr("requests.post", lambda url, json=None, timeout=None: FakeLLMResponse(response_data))

    item = Opportunity(id="1", kind="internship", title="Senior VP", url="http://x", source="s")
    result = enrich([item])
    assert len(result) == 0


def test_connection_error_leaves_items_unchanged(monkeypatch) -> None:
    """Connection error leaves all items unchanged."""
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")

    def raise_err(*args, **kwargs):
        raise requests.ConnectionError("Ollama offline")

    monkeypatch.setattr("requests.post", raise_err)

    item = Opportunity(id="1", kind="hackathon", title="Hack", url="http://x", source="s")
    result = enrich([item])
    assert len(result) == 1
    assert result[0].summary == ""
