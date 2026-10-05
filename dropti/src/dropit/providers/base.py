from __future__ import annotations

from typing import Protocol, Sequence

from dropit.models import Mode, Point


class TravelTimeProvider(Protocol):
    """Source de temps de trajet. Renvoie une matrice [source][cible] en minutes."""

    def durations(
        self, sources: Sequence[Point], targets: Sequence[Point], mode: Mode
    ) -> list[list[float]]: ...
