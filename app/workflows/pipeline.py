from __future__ import annotations

from app.adapters.llm.ollama_scan_extractor_adapter import OllamaScanExtractorAdapter
from app.adapters.storage.json_storage_adapter import JsonStorageAdapter
from app.adapters.url_resolver import UrlResolver
from app.adapters.zyte.zyte_fetcher_adapter import ZyteFetcherAdapter
from app.core.services.scraper_service import ScraperService
from app.core.utils.url_utils import get_base_url


def run_pipeline(
    start_url: str,
    output_path: str,
    limit: int | None = None,
    use_scan_llm: bool = True,
    ollama_model: str = "llama3.1:8b",
    ollama_base_url: str = "http://127.0.0.1:11434",
) -> int:
    fetcher = ZyteFetcherAdapter()
    repository = JsonStorageAdapter(path=output_path)
    base_url = get_base_url(start_url)
    url_resolver = UrlResolver(base_url)
    scan_extractor = None
    if use_scan_llm:
        scan_extractor = OllamaScanExtractorAdapter(model=ollama_model, base_url=ollama_base_url)
    service = ScraperService(fetcher, repository, url_resolver, scan_extractor=scan_extractor)
    return service.run(start_url=start_url, limit=limit)
