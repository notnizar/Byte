from __future__ import annotations

import os

from app.adapters.gemini.gemini_scan_extractor_adapter import GeminiScanExtractorAdapter
from app.adapters.storage.json_storage_adapter import JsonStorageAdapter
from app.adapters.url_resolver import UrlResolver
from app.adapters.zyte.zyte_fetcher_adapter import ZyteFetcherAdapter
from app.core.services.scraper_service import ScraperService
from app.core.utils.url_utils import get_base_url


def run_pipeline(
    start_url: str,
    output_path: str,
    limit: int | None = None,
    gemini_api_key: str | None = None,
    gemini_model: str = "gemini-3.1-flash-lite-preview",
) -> int:
    fetcher = ZyteFetcherAdapter()
    repository = JsonStorageAdapter(path=output_path)
    base_url = get_base_url(start_url)
    url_resolver = UrlResolver(base_url)
    api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "").strip()
    scan_extractor = GeminiScanExtractorAdapter(api_key=api_key, model=gemini_model) if api_key else None
    service = ScraperService(fetcher, repository, url_resolver, scan_extractor=scan_extractor)
    return service.run(start_url=start_url, limit=limit)
