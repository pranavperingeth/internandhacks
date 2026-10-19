"""Tests for models.py and config.py (Phase 1)."""

import os
import tempfile

import yaml

from oppwatch.models import Opportunity
from oppwatch.config import load_sources, load_filters


def test_opportunity_defaults():
    """Opportunity with only required fields has score == 0 and deadline is None."""
    opp = Opportunity(id="abc", kind="hackathon", title="Test", url="http://x", source="s")
    assert opp.score == 0
    assert opp.deadline is None
    assert opp.posted_at is None
    assert opp.org == ""
    assert opp.location == ""
    assert opp.description == ""
    assert opp.summary == ""


def test_to_dict_contains_title():
    """to_dict() returns a dict containing the key 'title'."""
    opp = Opportunity(id="abc", kind="hackathon", title="Hack", url="http://x", source="s")
    d = opp.to_dict()
    assert isinstance(d, dict)
    assert "title" in d
    assert d["title"] == "Hack"


def test_load_sources_filters_enabled():
    """load_sources on a YAML with one enabled and one disabled source returns exactly 1."""
    sources_data = {
        "sources": [
            {"name": "a", "type": "rss", "kind": "hackathon", "enabled": True, "url": "http://a.com"},
            {"name": "b", "type": "rss", "kind": "internship", "enabled": False, "url": "http://b.com"},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sources_data, f)
        path = f.name
    try:
        result = load_sources(path)
        assert len(result) == 1
        assert result[0]["name"] == "a"
    finally:
        os.unlink(path)


def test_load_sources_raises_on_missing_url():
    """load_sources raises ValueError when url is missing."""
    sources_data = {
        "sources": [
            {"name": "bad", "type": "rss", "kind": "hackathon", "enabled": True},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sources_data, f)
        path = f.name
    try:
        raised = False
        try:
            load_sources(path)
        except ValueError:
            raised = True
        assert raised, "Expected ValueError for missing url"
    finally:
        os.unlink(path)


def test_load_filters_defaults():
    """load_filters fills missing keys with defaults."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"kinds": ["hackathon"]}, f)
        path = f.name
    try:
        result = load_filters(path)
        assert result["kinds"] == ["hackathon"]
        assert "min_score" in result
        assert "max_age_days" in result
    finally:
        os.unlink(path)
