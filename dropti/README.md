# drOPit

Application pour automobilistes : où déposer un ami (en faisant un détour borné) pour qu'il rentre
plus vite chez lui, alors que le conducteur rentre directement chez lui.

**Périmètre MVP** : un passager, scénario fixe Gif-sur-Yvette → La Frette-sur-Seine (en voiture),
passager à destination de Gare Saint-Lazare, mode du passager `transport` ou `velo`, détour max en minutes.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[gurobi,dev]"   # la licence académique Gurobi est gratuite
pytest
python -m dropit --max-detour 15 --mode velo --provider fake
```

## Données réelles (provider r5)

Le moteur de calcul est [r5py](https://r5py.readthedocs.io) : voiture, transports en commun et vélo
avec un seul outil, en local (pas de quota d'API). Prérequis : Java JDK 21.

```bash
pip install -e ".[r5]"
mkdir -p data/r5
# OSM Île-de-France : https://download.geofabrik.de/europe/france/ile-de-france.html
#   -> data/r5/ile-de-france-latest.osm.pbf
# GTFS Île-de-France Mobilités (transport.data.gouv.fr, « Horaires prévus ... IDFM »)
#   -> data/r5/idfm-gtfs.zip
python -m dropit --max-detour 15 --mode transport --provider r5 --depart 2026-10-12T18:30
```

`--depart` doit tomber dans la période de validité du GTFS téléchargé.

## Structure

- `src/dropit/models.py` : types du domaine (Point, Problem, Solution, Mode)
- `src/dropit/providers/` : sources de temps de trajet (`fake` pour les tests, `r5` pour les vraies données)
- `src/dropit/timedata.py` : construction des matrices de temps (entrée des solveurs)
- `src/dropit/optim/` : énumération de référence et modèle Gurobi
- `src/dropit/service.py` : orchestration ; `cli.py` : ligne de commande
- `data/candidates_sample.csv` : points de dépose candidats (coordonnées approximatives)

## Limites connues du MVP

- Une seule heure de départ pour tous les candidats en transports en commun (en réalité, l'heure
  d'arrivée au point de dépose dépend du candidat).
- Temps de voiture sans trafic.

## Feuille de route

1. [x] Squelette, modèle, tests sur données synthétiques
2. [ ] Brancher r5py (OSM + GTFS IDFM) et valider les temps sur quelques trajets connus
3. [ ] Candidats générés depuis les arrêts du GTFS, filtrés par détour
4. [ ] Heure de départ propre à chaque candidat
5. [ ] Géocodage (API Adresse), API FastAPI, interface Streamlit
