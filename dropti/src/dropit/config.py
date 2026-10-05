from pathlib import Path

from dropit.models import Point

# Coordonnées approximatives pour le MVP.
# TODO: remplacer par un géocodage via l'API Adresse (data.gouv.fr).
ORIGIN = Point("Gif-sur-Yvette", 48.7006, 2.1339)
DRIVER_HOME = Point("La Frette-sur-Seine", 48.9739, 2.1717)
PASSENGER_HOME = Point("Gare Saint-Lazare", 48.8761, 2.3252)

# Données pour r5py (à télécharger, voir README) : non versionnées.
R5_DIR = Path("data/r5")
OSM_PBF = R5_DIR / "ile-de-france-latest.osm.pbf"
GTFS_FILES = [R5_DIR / "idfm-gtfs.zip"]
