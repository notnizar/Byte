from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Car:
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)
