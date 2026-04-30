from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.core.entities.car import Car
from app.core.ports.car_repository_port import CarRepositoryPort


class JsonStorageAdapter(CarRepositoryPort):
    def __init__(self, path: str = "cleaned.json") -> None:
        self.path = Path(path)
        if not self.path.exists():
            self._write([])

    def save(self, car: Car) -> None:
        items = self._read()
        items.append(car.to_dict())
        self._write(items)

    def _read(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, items: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")
