from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path

from dropit import config
from dropit.models import PASSENGER_MODES, Mode, Point, Problem
from dropit.providers.fake import FakeProvider
from dropit.service import solve


def load_candidates(path: Path) -> tuple[Point, ...]:
    with path.open(encoding="utf-8") as f:
        return tuple(Point(r["name"], float(r["lat"]), float(r["lon"])) for r in csv.DictReader(f))


def main() -> None:
    p = argparse.ArgumentParser(prog="dropit")
    p.add_argument("--max-detour", type=float, required=True, help="détour max du conducteur (min)")
    p.add_argument("--mode", choices=[m.value for m in PASSENGER_MODES], default=Mode.TRANSIT.value,
                   help="mode du passager après la dépose")
    p.add_argument("--candidates", type=Path, default=Path("data/candidates_sample.csv"))
    p.add_argument("--provider", choices=["fake", "r5"], default="fake")
    p.add_argument("--depart", type=dt.datetime.fromisoformat, default=dt.datetime(2026, 10, 12, 18, 30),
                   help="heure où le passager quitte la voiture (AAAA-MM-JJTHH:MM), pour r5")
    p.add_argument("--method", choices=["gurobi", "baseline"], default="gurobi")
    a = p.parse_args()

    if a.provider == "fake":
        provider = FakeProvider()
    else:
        from dropit.providers.r5 import R5Provider

        provider = R5Provider(config.OSM_PBF, config.GTFS_FILES, departure=a.depart)

    problem = Problem(
        origin=config.ORIGIN,
        driver_home=config.DRIVER_HOME,
        passenger_home=config.PASSENGER_HOME,
        candidates=load_candidates(a.candidates),
        max_detour_min=a.max_detour,
        passenger_mode=Mode(a.mode),
    )
    s = solve(problem, provider, method=a.method)
    print(f"Point de dépose : {s.dropoff.name}")
    print(f"Détour conducteur : {s.driver_detour_min:.1f} min (max {a.max_detour:.0f})")
    print(f"Trajet passager : {s.passenger_total_min:.1f} min "
          f"(gain de {s.passenger_gain_min:.1f} min vs dépose chez le conducteur)")


if __name__ == "__main__":
    main()
