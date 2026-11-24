import requests
import yaml
import json
from pathlib import Path
from datetime import datetime, date
from rich.console import Console
from rich.panel import Panel
from zoneinfo import ZoneInfo 

def init_parser(force: bool = False):
    config_dir = Path.home() / ".config" / "velo"
    config_file = config_dir / "config.yaml"
    data_dir = Path.home() / ".local" / "share" / "velo"

    default_config = {
        "network": {
            "name": "V'Lille",
            "gbfs_url": "https://media.ilevia.fr/opendata/gbfs.json",
        },
        "data": {
            "folder": str(data_dir),
        },
        "refresh": {
            "max_age_days": 7,
        },
        "collect": {
            "interval_seconds": 120,
        },
        "alerts": {
            "low_bikes": 2,
            "low_docks": 2,
        },
        "dashboard": {
            "refresh_seconds": 60,
        },
        "logging": {
            "level": "INFO",
        },
    }

    config_dir.mkdir(parents=True, exist_ok=True)

    if not config_file.exists() or force:
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)
        print(f"Configuration créée: {config_file}")
    else:
        print(f"Configuration déjà existante: {config_file}")

    # --- Création du dossier data --- #

    if not data_dir.exists():
        data_dir.mkdir(parents = True, exist_ok = True)
        print(f"Dossier de données créé : {data_dir}")

    # --- Téléchargement des 3 fichiers --- #

    response = []
    urls = ["https://media.ilevia.fr/opendata/station_information.json", "https://media.ilevia.fr/opendata/system_information.json", "https://media.ilevia.fr/opendata/vehicle_types.json"]
    for i in range(len(urls)):
        response.append(requests.get(urls[i]))
        response[i].raise_for_status()

    with open(f"{data_dir}/station_information.json", "wb") as file:
        file.write(response[0].content)
    with open(f"{data_dir}/system_information.json", "wb") as file:
        file.write(response[1].content)
    with open(f"{data_dir}/vehicle_types.json", "wb") as file:
        file.write(response[2].content)

    with open(f"{data_dir}/station_information.json", "rb") as file:
        data = json.load(file)
        stations = data.get("data").get("stations")
        stations_amount = len(stations)

    print(f"Connexion à V'Lille : OK ({stations_amount} stations)")

    

def station_list():
    url = "https://media.ilevia.fr/opendata/station_information.json"

    response = requests.get(url)

    if response.status_code == 200:
        stations = response.json()
        print("ID     Station")

        for station in stations["data"]["stations"]:
            print(f"{int(station['station_id']):03d}    {station['name']}")


def station_search(search: str):
    url = "https://media.ilevia.fr/opendata/station_information.json"

    response = requests.get(url)
    response.raise_for_status()

    stations = response.json()["data"]["stations"]

    print("ID     Station")

    search = search.lower().strip()
    found = False

    for station in stations:
        station_id = str(station["station_id"])
        station_name = station["name"].lower().strip()

        if search in station_id or search in station_name:
            print(f"{int(station_id):03d}    {station['name']}")
            found = True

    if not found:
        print("Aucune station trouvée.")



def refresh():
    data_dir = Path.home() / ".local" / "share" / "velo"

    response = []
    urls = ["https://media.ilevia.fr/opendata/station_information.json", "https://media.ilevia.fr/opendata/system_information.json", "https://media.ilevia.fr/opendata/vehicle_types.json"]
    for i in range(len(urls)):
        response.append(requests.get(urls[i]))
        response[i].raise_for_status()

    # Station_Information

    with open(f"{data_dir}/station_information.json", "wb") as file:
        file.write(response[0].content)
    with open(f"{data_dir}/station_information.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        stations = data.get("data").get("stations")
        stations_amount = len(stations)
        print(f"Last updated (station_information.json) : {date.fromtimestamp(date_timestamp)}")

    # System_Information

    with open(f"{data_dir}/system_information.json", "wb") as file:
        file.write(response[1].content)
    with open(f"{data_dir}/system_information.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        print(f"Last updated (system_information.json) : {date.fromtimestamp(date_timestamp)}")

    # Vehicle_Types

    with open(f"{data_dir}/vehicle_types.json", "wb") as file:
        file.write(response[2].content)
    with open(f"{data_dir}/vehicle_types.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        print(f"Last updated (vehicle_types.json) : {date.fromtimestamp(date_timestamp)}")



    print(f"Il y a {stations_amount} stations")








def velo_status():
    url_informations = "https://media.ilevia.fr/opendata/station_information.json"
    url_statuts = "https://media.ilevia.fr/opendata/station_status.json"

    response_informations = requests.get(url_informations)
    response_statuts = requests.get(url_statuts)

    informations = response_informations.json()["data"]["stations"]
    statuts = response_statuts.json()["data"]["stations"]

    statuts_par_id = {}

    for statut in statuts:
        station_id = statut["station_id"]
        statuts_par_id[station_id] = statut

    en_service = 0
    hors_service = 0
    vides = 0
    pleines = 0
    velos_disponibles = 0
    places_libres = 0

    for station in informations:
        station_id = station["station_id"]
        statut = statuts_par_id.get(station_id)

        if statut is None:
            continue

        if (statut["is_installed"] == 1 and statut["is_renting"] == 1 and statut["is_returning"] == 1):
            en_service += 1
        else:
            hors_service += 1

        velos = statut["num_bikes_available"]
        places = statut["num_docks_available"]

        if velos == 0:
            vides += 1

        if places == 0:
            pleines += 1

        velos_disponibles += velos
        places_libres += places

    capacite_totale = velos_disponibles + places_libres

    if capacite_totale > 0:
        taux_remplissage = round(
            velos_disponibles / capacite_totale * 100
        )
    else:
        taux_remplissage = 0

    print("V'Lille - Statistiques des stations")
    print()

    print("Stations          en service, ", en_service, "/", len(informations))
    print("                  hors service ", hors_service)
    print("                  vides ", vides)
    print("                  pleines", pleines)

    print()
    print("Vélos             disponibles ", velos_disponibles)
    print("                  places libres", places_libres)
    print("                  taux de remplissage", taux_remplissage, "%")
