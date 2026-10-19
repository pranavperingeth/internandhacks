"""Source type registry."""

from oppwatch.sources import rss, json_api, html_page

SOURCE_TYPES = {"rss": rss.fetch, "json_api": json_api.fetch, "html": html_page.fetch}
