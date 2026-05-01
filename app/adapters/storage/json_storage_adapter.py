from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.core.entities.car import Car
from app.core.ports.car_repository_port import CarRepositoryPort


class JsonStorageAdapter(CarRepositoryPort):
    def __init__(self, path: str = "cleaned.json") -> None:
        self.path = Path(path)
        self.state_path = self.path.with_suffix(".state.json")
        if not self.path.exists():
            self._write([])
        self.last_id = self._load_last_id()

    def save(self, car: Car) -> None:
        items = self._read()
        data = car.to_dict()
        if not data.get("id"):
            self.last_id += 1
            data["id"] = self.last_id
            self._save_last_id(self.last_id)
        else:
            current_id = _coerce_int(data.get("id"))
            if current_id and current_id > self.last_id:
                self.last_id = current_id
                self._save_last_id(self.last_id)
        items.append(_order_item(data))
        self._write(items)

    def _read(self) -> List[Dict[str, Any]]:
        try:
            content = self.path.read_text(encoding="utf-8").strip()
            if not content:
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def _write(self, items: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def _load_last_id(self) -> int:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                value = _coerce_int(data.get("last_id")) if isinstance(data, dict) else 0
                if value:
                    return value
            except (OSError, json.JSONDecodeError):
                pass

        max_id = 0
        for item in self._read():
            current_id = _coerce_int(item.get("id"))
            if current_id and current_id > max_id:
                max_id = current_id
        if max_id:
            self._save_last_id(max_id)
        return max_id

    def _save_last_id(self, value: int) -> None:
        payload = {"last_id": value}
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _coerce_int(value: Any) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _order_item(data: Dict[str, Any]) -> Dict[str, Any]:
    ordered: Dict[str, Any] = {}
    if "id" in data:
        ordered["id"] = data["id"]
    for key, value in data.items():
        if key == "id":
            continue
        ordered[key] = value
    return ordered
