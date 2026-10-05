from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    CAR = "voiture"      # mode du conducteur (fixe)
    TRANSIT = "transport"  # transports en commun (+ marche d'accès)
    BIKE = "velo"


# Modes que le passager peut choisir pour finir son trajet.
PASSENGER_MODES = (Mode.TRANSIT, Mode.BIKE)


@dataclass(frozen=True)
class Point:
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Problem:
    origin: Point            # O : départ commun
    driver_home: Point       # C : domicile du conducteur
    passenger_home: Point    # H : domicile du passager
    candidates: tuple[Point, ...]
    max_detour_min: float    # détour maximal accepté par le conducteur (minutes)
    passenger_mode: Mode     # mode du passager entre le point de dépose et H

    def __post_init__(self) -> None:
        if self.passenger_mode not in PASSENGER_MODES:
            raise ValueError(f"Mode passager invalide : {self.passenger_mode.value}")
        if self.max_detour_min < 0:
            raise ValueError("Le détour maximal doit être positif ou nul")


@dataclass(frozen=True)
class Solution:
    dropoff: Point
    passenger_total_min: float      # trajet du passager : O -> p en voiture, puis p -> H
    reference_passenger_min: float  # même trajet si on dépose chez le conducteur (détour nul)
    driver_detour_min: float

    @property
    def passenger_gain_min(self) -> float:
        return self.reference_passenger_min - self.passenger_total_min
