from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class UrlResolverPort(ABC):
    @abstractmethod
    def resolve_detail_url(self, listing: Dict[str, str]) -> str:
        raise NotImplementedError
