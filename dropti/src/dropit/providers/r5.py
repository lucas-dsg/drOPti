from __future__ import annotations

import datetime as dt
import math
from pathlib import Path
from typing import Sequence

from dropit.models import Mode, Point


class R5Provider:
    """Matrices de temps de trajet calculées en local avec r5py (moteur R5).

    Un seul moteur pour les trois modes (voiture, transports en commun, vélo), à partir
    d'un extrait OpenStreetMap et des GTFS : pas de quota d'API, résultats reproductibles.
    Nécessite Java (JDK 21) ; le réseau est construit une fois (quelques minutes en IDF).

    `departure` : heure de départ utilisée pour les calculs horaires (transports en commun).
    Approximation du MVP : une seule heure pour tous les candidats. Il faut donner l'heure
    à laquelle le passager quitte la voiture (≈ départ + une partie du trajet), dans la
    période couverte par le GTFS.
    """

    def __init__(
        self,
        osm_pbf: Path,
        gtfs_files: Sequence[Path],
        departure: dt.datetime,
        max_time_min: float = 180.0,
    ):
        self.osm_pbf = Path(osm_pbf)
        self.gtfs_files = [Path(g) for g in gtfs_files]
        self.departure = departure
        self.max_time_min = max_time_min
        self._network = None

    def _get_network(self):
        import r5py

        if self._network is None:
            self._network = r5py.TransportNetwork(self.osm_pbf, self.gtfs_files)
        return self._network

    def durations(
        self, sources: Sequence[Point], targets: Sequence[Point], mode: Mode
    ) -> list[list[float]]:
        import geopandas as gpd
        import r5py
        from shapely.geometry import Point as GeoPoint

        modes = {
            Mode.CAR: [r5py.TransportMode.CAR],
            Mode.TRANSIT: [r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            Mode.BIKE: [r5py.TransportMode.BICYCLE],
        }[mode]

        def to_gdf(pts: Sequence[Point]):
            return gpd.GeoDataFrame(
                {"id": list(range(len(pts)))},
                geometry=[GeoPoint(p.lon, p.lat) for p in pts],
                crs="EPSG:4326",
            )

        ttm = r5py.TravelTimeMatrix(
            self._get_network(),
            origins=to_gdf(sources),
            destinations=to_gdf(targets),
            departing=self.departure,
            transport_modes=modes,
            max_time=dt.timedelta(minutes=self.max_time_min),
        )
        times = {(int(r.from_id), int(r.to_id)): r.travel_time for r in ttm.itertuples()}

        matrix: list[list[float]] = []
        for i in range(len(sources)):
            row = []
            for j in range(len(targets)):
                v = times.get((i, j))
                # Trajet introuvable ou trop long : infini (candidat écarté plus loin).
                row.append(math.inf if v is None or math.isnan(v) else float(v))
            matrix.append(row)
        return matrix
