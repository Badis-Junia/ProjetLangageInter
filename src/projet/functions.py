import requests


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
