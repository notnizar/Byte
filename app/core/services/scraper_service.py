from __future__ import annotations

from typing import Any, Dict, Optional

from app.core.entities.car import Car
from app.core.ports.car_fetcher_port import CarFetcherPort
from app.core.ports.car_repository_port import CarRepositoryPort
from app.core.ports.scan_extractor_port import ScanExtractorPort
from app.core.ports.url_resolver_port import UrlResolverPort
from app.core.parsers.common import clean_text

from app.core.parsers.listing_parser import extract_fields
from app.core.parsers.search_parser import parse_listings
from app.core.utils.url_utils import get_base_url


class ScraperService:
    def __init__(
        self,
        fetcher: CarFetcherPort,
        repository: CarRepositoryPort,
        url_resolver: UrlResolverPort,
        scan_extractor: ScanExtractorPort | None = None,
    ) -> None:
        self.fetcher = fetcher
        self.repository = repository
        self.url_resolver = url_resolver
        self.scan_extractor = scan_extractor

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

            description = detail_fields.get("Description", "")
            analysis_text = description if description.strip() else clean_text(detail_html)
            condition = str(detail_fields.get("Condition", "")).strip().lower()
            if self.scan_extractor and analysis_text and condition == "used":
                try:
                    analysis = self.scan_extractor.analyze_description(analysis_text)
                    _merge_analysis(detail_fields, analysis)
                except Exception:
                    # Keep scraping working even if Gemini is unavailable.
                    pass

            data = _normalize_details(detail_fields)
            if not data.get("price") and listing.get("price"):
                data["price"] = listing["price"]
            if listing.get("url"):
                data["url"] = listing["url"]
            car = Car(data=data)
            self.repository.save(car)
            saved += 1

        return saved


def _normalize_details(details: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {
        "price",
        "Car Make",
        "Model",
        "Year",
        "Fuel",
        "Exterior Color",
        "Interior Color",
        "Neighborhood",
        "City",
        "Condition",
        "Kilometers",
        "Published Date",
        "url",
        "chassis_score",
        "front_left",
        "front_right",
        "rear_left",
        "rear_right",
        "used_in_apps",
    }
    return {key: value for key, value in details.items() if key in allowed and value is not None and value != ""}


def _merge_analysis(details: Dict[str, Any], analysis: Dict[str, Any]) -> None:
    field_map = {
        "chassis_score": "chassis_score",
        "front_left": "front_left",
        "front_right": "front_right",
        "rear_left": "rear_left",
        "rear_right": "rear_right",
        "used_in_apps": "used_in_apps",
    }
    for source_key, target_key in field_map.items():
        value = analysis.get(source_key)
        if value is not None and value != "":
            details[target_key] = value
