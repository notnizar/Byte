from __future__ import annotations

from app.adapters.storage.json_storage_adapter import JsonStorageAdapter
from app.adapters.url_resolver import UrlResolver
from app.adapters.zyte.zyte_fetcher_adapter import ZyteFetcherAdapter
from app.core.services.scraper_service import ScraperService
from app.core.utils.url_utils import get_base_url


def run_pipeline(start_url: str, output_path: str, limit: int | None = None) -> int:
    fetcher = ZyteFetcherAdapter()
    repository = JsonStorageAdapter(path=output_path)
    base_url = get_base_url(start_url)
    url_resolver = UrlResolver(base_url)
    service = ScraperService(fetcher, repository, url_resolver)
    return service.run(start_url=start_url, limit=limit)
