from __future__ import annotations

from abc import ABC, abstractmethod


class CarFetcherPort(ABC):
    @abstractmethod
    def fetch_listing_page_html(self, url: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def fetch_listing_detail_html(self, url: str) -> str:
        raise NotImplementedError
