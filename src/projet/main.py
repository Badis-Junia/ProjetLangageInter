import argparse

parser = argparse.ArgumentParser(description="Pour les vélos")

subparsers = parser.add_subparsers(dest="commmande", required=True)

init_parser = subparsers.add_parser("init", help="Prépare l'outil")
init_parser.add_argument("--force", action="store_true", help="Force l'initialisation")

subparsers.add_parser("refresh", help="Met à jour les données")

station_parser = subparsers.add_parser("station", help="Consulter une station")
station_subparsers = station_parser.add_subparsers(dest="station_commande", required=True)
station_subparsers.add_parser("list", help="Liste toutes les stations")
search_parser = station_subparsers.add_parser("search", help="Recherche une station")
search_parser.add_argument("nom", help="Nom de la station à rechercher")

subparsers.add_parser("status", help="Résumé de l'état du réseau en temps réel")

subparsers.add_parser("favorites", help="Ajouter, enlever des favories")

alert_parser = subparsers.add_parser("alerts", help="Lister les stations vides, presque vides, bref toute les alertes")
alert_parser.add_argument("--low-bikes", type=int)
alert_parser.add_argument("--low-docks", type=int)

subparsers.add_parser("dashboard", help="Tableau de bord, mis à jour en temps réel")

subparsers.add_parser("collect", help="Enregistre l'état de toute les stations à intervalle régulier")

subparsers.add_parser("history", help="Affiche les périodes et relevés enregistrés")

subparsers.add_parser("query", help="Analyser l'historique enregistré")

args = parser.parse_args()
