"""HTML page source plugin: scrape plain-HTML pages using CSS selectors."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from oppwatch import net
from oppwatch.models import Opportunity
from oppwatch.normalize import make_opportunity

logger = logging.getLogger(__name__)


def fetch(cfg: dict) -> list[Opportunity]:
    """Fetch an HTML page and extract listings using CSS selectors."""
    url = cfg["url"]
    kind = cfg["kind"]
    source = cfg["name"]
    item_selector = cfg["item_selector"]
    fields = cfg.get("fields", {})
    resp = net.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(item_selector)
    results: list[Opportunity] = []
    for item in items:
        raw: dict[str, str] = {}
        for field_name, sel in fields.items():
            if not sel:
                continue
            if field_name == "url":
                el = item.select_one(sel)
                if el:
                    href = el.get("href", "")
                    if not href and el.name == "a":
                        href = el.get("href", "")
                    raw["url"] = urljoin(url, href) if href else ""
                else:
                    raw["url"] = ""
            else:
                el = item.select_one(sel)
                if el:
                    raw[field_name] = el.get_text(" ", strip=True)
                else:
                    raw[field_name] = ""
        # If no url field selector but title selector found a link, use that
        if "url" not in raw or not raw.get("url"):
            title_sel = fields.get("title", "")
            if title_sel:
                el = item.select_one(title_sel)
                if el:
                    a_tag = el.find("a") if el.name != "a" else el
                    if a_tag and a_tag.get("href"):
                        raw["url"] = urljoin(url, a_tag["href"])
        opp = make_opportunity(raw, kind, source)
        if opp is not None:
            results.append(opp)
    logger.info("HTML source '%s': fetched %d items", source, len(results))
    return results
