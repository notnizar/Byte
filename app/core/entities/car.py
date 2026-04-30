from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Car:
    listing_id: str
    title: str
    price: str
    currency: str
    location: str
    url: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.listing_id,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "location": self.location,
            "url": self.url,
            **self.details,
        }
