import requests
import yaml
import json
from pathlib import Path
from datetime import date


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


def station_list():
    url = "https://media.ilevia.fr/opendata/station_information.json"

    response = requests.get(url)

    if response.status_code == 200:
        stations = response.json()
        print("ID     Station")

        for station in stations["data"]["stations"]:
            print(f"{int(station['station_id']):03d}    {station['name']}")


def station_search(name: str):
    url = "https://media.ilevia.fr/opendata/station_information.json"

    param = {"name": name}
    response = requests.get(url, param)

    if response.status_code == 200:
        stations = response.json()
        print("ID     Station")

        for station in stations["data"]["stations"]:
            if name in station["name"].lower().strip():
                print(f"{int(station['station_id']):03d}    {station['name']}")


# --- Refresh --- #

def refresh():
    response = []
    urls = ["https://media.ilevia.fr/opendata/station_information.json", "https://media.ilevia.fr/opendata/system_information.json", "https://media.ilevia.fr/opendata/vehicle_types.json"]
    for i in range(len(urls)):
        response.append(requests.get(urls[i]))
        response[i].raise_for_status()

    # Station_Information

    with open("data/station_information.json", "wb") as file:
        file.write(response[0].content)
    with open("data/station_information.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        stations = data.get("data").get("stations")
        stations_amount = len(stations)
        print(f"Last updated (station_information.json) : {date.fromtimestamp(date_timestamp)}")

    # System_Information

    with open("data/system_information.json", "wb") as file:
        file.write(response[1].content)
    with open("data/system_information.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        print(f"Last updated (system_information.json) : {date.fromtimestamp(date_timestamp)}")

    # Vehicle_Types

    with open("data/vehicle_types.json", "wb") as file:
        file.write(response[2].content)
    with open("data/vehicle_types.json", "rb") as file:
        data = json.load(file)
        date_timestamp = data.get("last_updated")
        print(f"Last updated (vehicle_types.json) : {date.fromtimestamp(date_timestamp)}")

    print(f"Il y a {stations_amount} stations")

