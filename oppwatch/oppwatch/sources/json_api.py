"""JSON API source plugin: fetch structured JSON endpoints (GET or POST)."""

import logging
from typing import Any

from oppwatch import net
from oppwatch.models import Opportunity
from oppwatch.normalize import make_opportunity

logger = logging.getLogger(__name__)


def get_path(obj: Any, path: str) -> Any:
    """Navigate a dot-separated path into a nested dict. Return None if any part is missing."""
    if not path:
        return obj
    for key in path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj


def _extract_value(val: Any) -> str:
    """Convert a value to string: join lists, skip dicts/None."""
    if val is None:
        return ""
    if isinstance(val, list):
        return ", ".join(str(v) for v in val if v is not None)
    if isinstance(val, dict):
        return ""
    return str(val)


def fetch(cfg: dict) -> list[Opportunity]:
    """Fetch a JSON API and return normalized Opportunity objects."""
    url = cfg["url"]
    kind = cfg["kind"]
    source = cfg["name"]
    items_path = cfg.get("items_path", "")
    field_map = cfg.get("field_map", {})
    where = cfg.get("where", {})
    method = cfg.get("method", "get").lower()

    if method == "post":
        json_body = cfg.get("json_body", {})
        resp = net.post(url, json_body=json_body, headers=cfg.get("headers"))
    else:
        resp = net.get(url, params=cfg.get("params"), headers=cfg.get("headers"))

    data = resp.json()
    items = get_path(data, items_path)
    if not isinstance(items, list):
        raise ValueError(f"items_path '{items_path}' did not resolve to a list in source '{source}'")
    if where:
        items = [item for item in items if all(item.get(k) == v for k, v in where.items())]

    url_template = cfg.get("url_template")
    url_prefix = cfg.get("url_prefix")

    results: list[Opportunity] = []
    for item in items:
        raw: dict[str, Any] = {}
        for our_field, json_path in field_map.items():
            val = get_path(item, json_path)
            raw[our_field] = _extract_value(val)
        if "url" in raw and raw["url"]:
            if url_template:
                raw["url"] = url_template.format(raw["url"])
            elif url_prefix and not raw["url"].startswith("http"):
                raw["url"] = url_prefix + raw["url"]
        opp = make_opportunity(raw, kind, source)
        if opp is not None:
            results.append(opp)
    logger.info("JSON API source '%s': fetched %d items", source, len(results))
    return results
