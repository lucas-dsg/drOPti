import pytest

from dropit.models import Point
from dropit.optim.baseline import solve_baseline
from dropit.timedata import TimeData


def make_td(max_detour: float) -> TimeData:
    pts = tuple(Point(n, 0, 0) for n in ("A", "B", "C", "Maison"))
    return TimeData(
        candidates=pts,
        driver_home_index=3,
        t_oc=30.0,
        t_op=(10.0, 20.0, 25.0, 30.0),
        t_pc=(25.0, 18.0, 15.0, 0.0),   # détours : 5, 8, 10, 0
        t_ph=(40.0, 25.0, 10.0, 60.0),  # passager : 50, 45, 35, 90
        max_detour_min=max_detour,
    )


@pytest.mark.parametrize("max_detour,expected", [(0, 3), (5, 0), (8, 1), (10, 2), (60, 2)])
def test_baseline(max_detour, expected):
    assert solve_baseline(make_td(max_detour)) == expected


@pytest.mark.parametrize("max_detour", [0, 5, 8, 10, 60])
def test_gurobi_matches_baseline(max_detour):
    pytest.importorskip("gurobipy")
    from dropit.optim.gurobi_model import solve_gurobi

    td = make_td(max_detour)
    assert td.passenger_time(solve_gurobi(td)) == td.passenger_time(solve_baseline(td))


def test_unreachable_candidate_is_ignored():
    import dataclasses
    import math

    td = dataclasses.replace(make_td(60), t_ph=(40.0, 25.0, math.inf, 60.0))
    assert solve_baseline(td) == 1  # le candidat 2 (le meilleur) est injoignable
    pytest.importorskip("gurobipy")
    from dropit.optim.gurobi_model import solve_gurobi

    assert solve_gurobi(td) == 1


def test_problem_rejects_car_for_passenger():
    from dropit.models import Mode, Point, Problem

    p = Point("x", 0, 0)
    with pytest.raises(ValueError):
        Problem(p, p, p, (), 10, Mode.CAR)


def test_fake_provider_modes():
    from dropit.models import Mode, Point
    from dropit.providers.fake import FakeProvider

    a, b = Point("a", 48.0, 2.0), Point("b", 48.1, 2.1)
    fp = FakeProvider()
    car, bike = (fp.durations([a], [b], m)[0][0] for m in (Mode.CAR, Mode.BIKE))
    assert car < bike
