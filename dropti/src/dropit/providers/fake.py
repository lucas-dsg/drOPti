from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Sequence

from dropit.models import Mode, Point


def haversine_km(a: Point, b: Point) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (a.lat, a.lon, b.lat, b.lon))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(h))


class FakeProvider:
    """Temps approximatifs à vol d'oiseau : pour les tests et le développement hors ligne."""

    SPEED_KMH = {Mode.CAR: 40.0, Mode.TRANSIT: 25.0, Mode.BIKE: 15.0}
    TRANSIT_WAIT_MIN = 5.0

    def durations(
        self, sources: Sequence[Point], targets: Sequence[Point], mode: Mode
    ) -> list[list[float]]:
        return [[self._one(s, t, mode) for t in targets] for s in sources]

    def _one(self, a: Point, b: Point, mode: Mode) -> float:
        d = haversine_km(a, b)
        if d == 0:
            return 0.0
        minutes = d / self.SPEED_KMH[mode] * 60
        return minutes + (self.TRANSIT_WAIT_MIN if mode is Mode.TRANSIT else 0.0)
