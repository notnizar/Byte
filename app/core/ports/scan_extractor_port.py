from __future__ import annotations

from abc import ABC, abstractmethod


class ScanExtractorPort(ABC):
    @abstractmethod
    def extract_scan(self, description: str) -> str:
        raise NotImplementedError
