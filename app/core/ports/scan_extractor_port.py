from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ScanExtractorPort(ABC):
    @abstractmethod
    def analyze_description(self, description: str) -> Dict[str, Any]:
        raise NotImplementedError

    def extract_scan(self, description: str) -> str:
        analysis = self.analyze_description(description)
        return str(analysis.get("scan", "")).strip()
