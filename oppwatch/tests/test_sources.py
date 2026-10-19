"""Tests for source plugins (Phase 3)."""

import json
from pathlib import Path

import pytest

from oppwatch.sources import rss, json_api, html_page

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    """Fake requests.Response for monkeypatching net.get."""

    def __init__(self, content: bytes = b"", text: str = "", json_data=None):
        """Initialize with raw bytes, text, and/or parsed JSON."""
        self.content = content
        self.text = text
        self._json_data = json_data
        self.status_code = 200

    def json(self):
        """Return pre-loaded JSON data."""
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)


def _make_fake_get(fixture_path: Path):
    """Return a fake net.get that returns fixture content."""
    raw = fixture_path.read_bytes()
    text = fixture_path.read_text(encoding="utf-8")
    json_data = None
    if fixture_path.suffix == ".json":
        json_data = json.loads(text)

    def fake_get(url, params=None, headers=None, **kwargs):
        """Return a FakeResponse from fixture data."""
        return FakeResponse(content=raw, text=text, json_data=json_data)

    return fake_get


def test_rss_returns_two_opportunities(monkeypatch):
    """RSS returns 2 Opportunities with the right kind and source."""
    monkeypatch.setattr("oppwatch.sources.rss.net.get", _make_fake_get(FIXTURES / "sample.rss"))
    cfg = {"name": "test_rss", "type": "rss", "kind": "hackathon", "url": "http://fake.rss"}
    results = rss.fetch(cfg)
    assert len(results) == 2
    assert all(r.kind == "hackathon" for r in results)
    assert all(r.source == "test_rss" for r in results)


def test_json_where_filter(monkeypatch):
    """JSON with where: {active: true} returns 2 (not 3)."""
    monkeypatch.setattr("oppwatch.sources.json_api.net.get", _make_fake_get(FIXTURES / "sample.json"))
    cfg = {
        "name": "test_json",
        "type": "json_api",
        "kind": "hackathon",
        "url": "http://fake.json",
        "items_path": "hackathons",
        "where": {"active": True},
        "field_map": {
            "title": "title",
            "url": "url",
            "location": "displayed_location.location",
            "deadline": "submission_period_dates",
            "org": "organization_name",
        },
    }
    results = json_api.fetch(cfg)
    assert len(results) == 2


def test_json_dotted_path_and_list_join(monkeypatch):
    """JSON field_map with a dotted path works, and a list is joined with ', '."""
    from oppwatch.sources.json_api import get_path, _extract_value
    obj = {"a": {"b": {"c": "deep_value"}}}
    assert get_path(obj, "a.b.c") == "deep_value"
    assert _extract_value(["New York", "London"]) == "New York, London"


def test_html_returns_two_with_absolute_urls(monkeypatch):
    """HTML returns 2 items with absolute URLs."""
    monkeypatch.setattr("oppwatch.sources.html_page.net.get", _make_fake_get(FIXTURES / "sample.html"))
    cfg = {
        "name": "test_html",
        "type": "html",
        "kind": "hackathon",
        "url": "https://example.com/listings",
        "item_selector": "div.listing",
        "fields": {
            "title": "h3.title",
            "url": "h3.title a",
            "org": "span.org",
            "deadline": "span.deadline",
        },
    }
    results = html_page.fetch(cfg)
    assert len(results) == 2
    for r in results:
        assert r.url.startswith("https://example.com/")


def test_json_missing_items_path_raises(monkeypatch):
    """A wrong items_path key raises ValueError."""
    text = '{"data": [{"title": "x"}]}'
    fake = FakeResponse(content=text.encode(), text=text, json_data=json.loads(text))
    monkeypatch.setattr("oppwatch.sources.json_api.net.get", lambda *a, **kw: fake)
    cfg = {
        "name": "bad",
        "type": "json_api",
        "kind": "hackathon",
        "url": "http://fake",
        "items_path": "wrong_key",
        "field_map": {"title": "title", "url": "url"},
    }
    with pytest.raises(ValueError):
        json_api.fetch(cfg)
