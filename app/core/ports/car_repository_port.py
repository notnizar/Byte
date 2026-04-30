from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.entities.car import Car


class CarRepositoryPort(ABC):
    @abstractmethod
    def save(self, car: Car) -> None:
        raise NotImplementedError
