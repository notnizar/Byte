from __future__ import annotations

from typing import Dict, Optional

from app.core.entities.car import Car
from app.core.ports.car_fetcher_port import CarFetcherPort
from app.core.ports.car_repository_port import CarRepositoryPort
from app.core.ports.url_resolver_port import UrlResolverPort

from app.core.parsers.listing_parser import extract_fields
from app.core.parsers.search_parser import parse_listings
from app.core.utils.url_utils import get_base_url


class ScraperService:
    def __init__(
        self,
        fetcher: CarFetcherPort,
        repository: CarRepositoryPort,
        url_resolver: UrlResolverPort,
    ) -> None:
        self.fetcher = fetcher
        self.repository = repository
        self.url_resolver = url_resolver

    def run(self, start_url: str, limit: Optional[int] = None) -> int:
        listing_html = self.fetcher.fetch_listing_page_html(start_url)
        base_url = get_base_url(start_url)
        listings = parse_listings(listing_html, base_url)
        if limit is not None:
            listings = listings[:limit]

        saved = 0
        for listing in listings:
            detail_url = self.url_resolver.resolve_detail_url(listing)
            if not detail_url:
                continue
            try:
                detail_html = self.fetcher.fetch_listing_detail_html(detail_url)
                detail_fields = extract_fields(detail_html)
            except Exception:
                continue

            car = Car(
                listing_id=listing.get("id", ""),
                title=listing.get("title", ""),
                price=listing.get("price", ""),
                currency=listing.get("currency", ""),
                location=listing.get("location", ""),
                url=detail_url,
                details=_normalize_details(detail_fields),
            )
            self.repository.save(car)
            saved += 1

        return saved


def _normalize_details(details: Dict[str, str]) -> Dict[str, str]:
    return {key: value for key, value in details.items() if value}
