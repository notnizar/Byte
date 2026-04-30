from __future__ import annotations

from typing import Dict

from app.core.ports.url_resolver_port import UrlResolverPort


class UrlResolver(UrlResolverPort):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/") if base_url else ""

    def resolve_detail_url(self, listing: Dict[str, str]) -> str:
        url = listing.get("url", "")
        if url:
            return url
        listing_id = listing.get("id", "")
        if not listing_id:
            return ""
        if not self.base_url:
            return ""
        return f"{self.base_url}/en/search/{listing_id}"
