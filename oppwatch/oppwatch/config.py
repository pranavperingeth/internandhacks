"""Configuration loading for sources and filters."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


_DOTENV_LOADED = False

_FILTER_DEFAULTS = {
    "kinds": ["hackathon", "internship"],
    "include_keywords": [],
    "exclude_keywords": [],
    "preferred_locations": [],
    "min_score": 2,
    "max_age_days": 45,
    "drop_past_deadlines": True,
    "max_items_per_kind_in_digest": 25,
}

_REQUIRED_SOURCE_KEYS = {"name", "type", "kind", "url"}


def load_sources(path: str = "config/sources.yaml") -> list[dict]:
    """Return only sources with enabled == true. Raise ValueError if a source lacks name/type/kind/url."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    sources = data.get("sources", [])
    enabled = []
    for src in sources:
        missing = _REQUIRED_SOURCE_KEYS - set(src.keys())
        if missing:
            raise ValueError(f"Source {src.get('name', '?')} missing keys: {missing}")
        if src.get("enabled", False):
            enabled.append(src)
    return enabled


def load_filters(path: str = "config/filters.yaml") -> dict:
    """Return the filters dict. Fill missing keys with the defaults from filters.yaml."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    result = dict(_FILTER_DEFAULTS)
    result.update(data)
    return result


def get_env(name: str, default: str = "") -> str:
    """Read an environment variable (after load_dotenv() was called once at startup)."""
    global _DOTENV_LOADED
    if not _DOTENV_LOADED:
        load_dotenv()
        _DOTENV_LOADED = True
    return os.environ.get(name, default)
