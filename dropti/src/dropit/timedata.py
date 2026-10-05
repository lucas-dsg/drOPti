from __future__ import annotations

import math
from dataclasses import dataclass

from dropit.models import Mode, Point, Problem
from dropit.providers.base import TravelTimeProvider


@dataclass(frozen=True)
class TimeData:
    """Données numériques pures passées aux solveurs (minutes)."""

    candidates: tuple[Point, ...]
    driver_home_index: int
    t_oc: float                 # trajet direct O -> C en voiture
    t_op: tuple[float, ...]     # O -> p en voiture
    t_pc: tuple[float, ...]     # p -> C en voiture
    t_ph: tuple[float, ...]     # p -> H dans le mode du passager
    max_detour_min: float

    def detour(self, i: int) -> float:
        return self.t_op[i] + self.t_pc[i] - self.t_oc

    def passenger_time(self, i: int) -> float:
        return self.t_op[i] + self.t_ph[i]

    def usable(self, i: int) -> bool:
        """Tous les temps du candidat sont connus (trajet trouvé par le provider)."""
        return all(math.isfinite(t) for t in (self.t_op[i], self.t_pc[i], self.t_ph[i]))

    def feasible(self, i: int, tol: float = 1e-9) -> bool:
        return self.usable(i) and self.detour(i) <= self.max_detour_min + tol


def build_time_data(problem: Problem, provider: TravelTimeProvider) -> TimeData:
    # On ajoute toujours le domicile du conducteur : détour nul, donc il existe
    # toujours une solution réalisable (sauf si H est injoignable dans le mode choisi).
    cands = [c for c in problem.candidates if c.name != problem.driver_home.name]
    cands.append(problem.driver_home)
    home_idx = len(cands) - 1

    o, c, h = problem.origin, problem.driver_home, problem.passenger_home
    t_oc = provider.durations([o], [c], Mode.CAR)[0][0]
    t_op = provider.durations([o], cands, Mode.CAR)[0]
    t_pc = [row[0] for row in provider.durations(cands, [c], Mode.CAR)]
    t_ph = [row[0] for row in provider.durations(cands, [h], problem.passenger_mode)]

    return TimeData(
        candidates=tuple(cands),
        driver_home_index=home_idx,
        t_oc=t_oc,
        t_op=tuple(t_op),
        t_pc=tuple(t_pc),
        t_ph=tuple(t_ph),
        max_detour_min=problem.max_detour_min,
    )
