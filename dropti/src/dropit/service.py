from __future__ import annotations

from dropit.models import Problem, Solution
from dropit.providers.base import TravelTimeProvider
from dropit.timedata import TimeData, build_time_data


def make_solution(td: TimeData, i: int) -> Solution:
    return Solution(
        dropoff=td.candidates[i],
        passenger_total_min=td.passenger_time(i),
        reference_passenger_min=td.passenger_time(td.driver_home_index),
        driver_detour_min=td.detour(i),
    )


def solve(problem: Problem, provider: TravelTimeProvider, method: str = "gurobi") -> Solution:
    td = build_time_data(problem, provider)
    if method == "gurobi":
        from dropit.optim.gurobi_model import solve_gurobi

        idx = solve_gurobi(td)
    elif method == "baseline":
        from dropit.optim.baseline import solve_baseline

        idx = solve_baseline(td)
    else:
        raise ValueError(f"Méthode inconnue : {method}")
    return make_solution(td, idx)
