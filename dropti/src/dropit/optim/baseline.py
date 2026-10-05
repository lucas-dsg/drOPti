from __future__ import annotations

from dropit.timedata import TimeData


def solve_baseline(td: TimeData) -> int:
    """Énumération : renvoie l'indice du meilleur candidat réalisable."""
    feasible = [i for i in range(len(td.candidates)) if td.feasible(i)]
    if not feasible:
        raise ValueError("Aucun point de dépose réalisable")
    return min(feasible, key=td.passenger_time)
