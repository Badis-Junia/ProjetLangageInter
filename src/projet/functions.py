import requests
import yaml
import json
from pathlib import Path
from datetime import datetime, date
from rich.console import Console
from rich.panel import Panel
from zoneinfo import ZoneInfo
from rich.live import Live
from rich.table import Table
import time


PROJECT_DIR = Path(__file__).parent



# ----------------------------------------------------------------------------


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
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"Dossier de données créé : {data_dir}")

    # --- Téléchargement des 3 fichiers --- #

    response = []
    urls = [
        "https://media.ilevia.fr/opendata/station_information.json",
        "https://media.ilevia.fr/opendata/system_information.json",
        "https://media.ilevia.fr/opendata/vehicle_types.json",
    ]
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


# ----------------------------------------------------------------------------


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


# ----------------------------------------------------------------------------


def refresh(afficher: bool = True):
    data_dir = Path.home() / ".local" / "share" / "velo"

    response = []
    urls = [
        "https://media.ilevia.fr/opendata/station_information.json",
        "https://media.ilevia.fr/opendata/system_information.json",
        "https://media.ilevia.fr/opendata/vehicle_types.json",
    ]
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
        if afficher:
            print(
                f"Last updated (station_information.json) : {date.fromtimestamp(date_timestamp)}"
            )

    # System_Information

    with open(f"{data_dir}/system_information.json", "wb") as file:
        file.write(response[1].content)
    with open(f"{data_dir}/system_information.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        if afficher:
            print(
                f"Last updated (system_information.json) : {date.fromtimestamp(date_timestamp)}"
            )

    # Vehicle_Types

    with open(f"{data_dir}/vehicle_types.json", "wb") as file:
        file.write(response[2].content)
    with open(f"{data_dir}/vehicle_types.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        if afficher:
            print(
                f"Last updated (vehicle_types.json) : {date.fromtimestamp(date_timestamp)}"
            )

    if afficher:
        print(f"Il y a {stations_amount} stations")


# ----------------------------------------------------------------------------


def velo_status(afficher: bool = True):
    data_dir = Path.home() / ".local" / "share" / "velo"

    url_statuts = "https://media.ilevia.fr/opendata/station_status.json"

    response = requests.get(url_statuts)
    response.raise_for_status()

    status_file = data_dir / "station_status.json"

    with open(status_file, "wb") as file:
        file.write(response.content)

    with open(data_dir / "station_information.json", "r", encoding="utf-8") as file:
        informations = json.load(file)["data"]["stations"]

    with open(status_file, "r", encoding="utf-8") as file:
        statuts = json.load(file)["data"]["stations"]

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

        if (
            statut["is_installed"] == 1
            and statut["is_renting"] == 1
            and statut["is_returning"] == 1
        ):
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
        taux_remplissage = round(velos_disponibles / capacite_totale * 100)
    else:
        taux_remplissage = 0

    stats = {
        "total_stations": len(informations),
        "en_service": en_service,
        "hors_service": hors_service,
        "vides": vides,
        "pleines": pleines,
        "velos_disponibles": velos_disponibles,
        "places_libres": places_libres,
        "taux_remplissage": taux_remplissage,
    }

    if afficher:
        print("V'Lille - Statistiques des stations")
        print()

        print("Stations          en service     ", en_service, "/", len(informations))
        print("                  hors service    ", hors_service)
        print("                  vides            ", vides)
        print("                  pleines          ", pleines)

        print()
        print("Vélos             disponibles      ", velos_disponibles)
        print("                  places libres     ", places_libres)
        print("                  taux de remplissage", taux_remplissage, "%")

    return stats


# ----------------------------------------------------------------------------

FAVORITES_FILE = PROJECT_DIR / "favorites" / "favorites.json"

def favorite_state():
    print(f"{'ID'}    {'Station':<20} {'Vélos':>6}  {'Places':>6}")
    with open(FAVORITES_FILE, "r", encoding="utf-8") as jsonfile:
        favorites = json.load(jsonfile)
        for station_name, station in list(favorites.items()):
            velos = station.get("num_bikes_available")
            places = station.get("num_docks_available")
            if velos == 0:
                etat = "vide"
            if places == 0:
                etat = "plein"
            else:
                etat = ""

            print(
                f"{int(station['station_id']):03d}   {station_name:<20} {velos:>6}  {places:>6}  {etat}"
            )


def favorite_add(id: int):
    urls = [
        "https://media.ilevia.fr/opendata/station_status.json",
        "https://media.ilevia.fr/opendata/station_information.json",
    ]
    param = {"station_id": id}
    response = []

    for i in range(len(urls)):
        response.append(requests.get(urls[i], param))
        response[i].raise_for_status()

    status_stations = response[0].json()["data"]["stations"]
    information_stations = response[1].json()["data"]["stations"]
    station_names = {
        str(station["station_id"]): station["name"] for station in information_stations
    }

    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if FAVORITES_FILE.exists():
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {}

    if any(str(station.get("station_id")) == str(id) for station in data.values()):
        print("Cette station est déjà dans vos favoris.")
        raise ValueError("Station déjà présente dans le fichier favorites.json")
    if len(data) >= 10:
        print("Vous possédez plus de 10 favoris, veuillez en retirer un.")
        raise ValueError("Limite de favoris atteinte.")

    for station in status_stations:
        if str(id) == str(station["station_id"]):
            favoritePath = FAVORITES_FILE
            favoritePath.parent.mkdir(parents=True, exist_ok=True)

            if favoritePath.exists():
                try:
                    with favoritePath.open() as jsonfile:
                        favorites = json.load(jsonfile)
                except json.JSONDecodeError:
                    favorites = {}
            else:
                favorites = {}

            station_name = station_names.get(str(station["station_id"]))
            if station_name is None:
                return

            favorites[station_name] = station
            with favoritePath.open("w") as jsonfile:
                json.dump(favorites, jsonfile, indent=2)
            return


def favorite_delete(id: int):
    if not FAVORITES_FILE.exists():
        print("Aucun fichier de favoris n'existe pour le moment.")
        return

    with open(FAVORITES_FILE, "r", encoding="utf-8") as jsonfile:
        favorites = json.load(jsonfile)

    found = False
    for station_name, station in list(favorites.items()):
        if str(station.get("station_id")) == str(id):
            del favorites[station_name]
            found = True
            break

    if not found:
        print("Cette station n'est pas dans vos favoris.")
        raise ValueError("Station absente du fichier favorites.json")

    with open(FAVORITES_FILE, "w", encoding="utf-8") as jsonfile:
        json.dump(favorites, jsonfile, indent=2)


# ----------------------------------------------------------------------------


def velo_alerts(test):
    if test == 1:
        print("test 1")
    elif test == 2:
        print("test 2")
    elif test == 3:
        print("test 3")


def dashboard():
    console = Console()
    data_dir = Path.home() / ".local" / "share" / "velo"
    config_dir = Path.home() / ".config" / "velo"
    config_file = config_dir / "config.yaml"

    refresh(False)

    with open(data_dir / "system_information.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
        refresh_time = config.get("dashboard", {}).get("refresh_seconds", 60)

    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if FAVORITES_FILE.exists():
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            favoris_json = json.load(file)
    else:
        favoris_json = {}

    if refresh_time < 60:
        refresh_time = 60

    network_name = data["data"]["name"]
    network_last_updated = datetime.fromtimestamp(
        data["last_updated"], tz=ZoneInfo("Europe/Paris")
    ).strftime("%d/%m/%Y %H:%M:%S")

    stats = velo_status(afficher=False)
    temps_restant = refresh_time

    def generer_panneau(stats_actuelles, network_last_updated, secondes_restantes):

        texte_fav = ""

        for nom_station, infos in favoris_json.items():
            stations_id = infos["station_id"]
            velos = infos["num_bikes_available"]
            places = infos["num_docks_available"]
            texte_fav += f" - {nom_station} ({stations_id}) : {velos} velos, {places} places disponibles\n"

        return Panel.fit(
            f"[bold cyan]Réseau {network_name}[/bold cyan]\n"
            f"[dim]Mise à jour : {network_last_updated}[/dim]\n\n"
            f"[bold]Stations :[/bold] {stats_actuelles['en_service']}/{stats_actuelles['total_stations']} en service "
            f"({stats_actuelles['vides']} vides, {stats_actuelles['pleines']} pleines)\n"
            f"[bold]Vélos :[/bold] {stats_actuelles['velos_disponibles']} dispos | "
            f"{stats_actuelles['places_libres']} places ({stats_actuelles['taux_remplissage']}%)\n\n"
            f"Mes favoris :\n"
            f"{texte_fav}"
            f"Prochain rafraîchissement dans : [bold yellow]{secondes_restantes}s[/bold yellow]"
        )

    with Live(
        generer_panneau(stats, network_last_updated, temps_restant),
        console=console,
        refresh_per_second=4,
    ) as live:
        try:
            while True:
                time.sleep(1)
                temps_restant -= 1

                if temps_restant <= 0:
                    stats = velo_status(afficher=False)
                    with open(
                        data_dir / "station_status.json", "r", encoding="utf-8"
                    ) as f:
                        status_data = json.load(f)

                    network_last_updated = datetime.fromtimestamp(
                        status_data["last_updated"], tz=ZoneInfo("Europe/Paris")
                    ).strftime("%d/%m/%Y %H:%M:%S")

                    temps_restant = refresh_time

                live.update(generer_panneau(stats, network_last_updated, temps_restant))
        except KeyboardInterrupt:
            pass



