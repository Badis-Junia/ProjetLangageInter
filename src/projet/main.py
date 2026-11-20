import argparse

parser = argparse.ArgumentParser(description="Pour les vélos")

subparsers = parser.add_subparsers(dest="commmande", required=True)

init_parser = subparsers.add_parser("init", help="Prépare l'outil")
init_parser.add_argument("--force", action="store_true", help="Force l'initialisation")

subparsers.add_parser("refresh", help="Met à jour les données")
subparsers.add_parser("station", help="Consulter une station")
subparsers.add_parser("status", help="Résumé de l'état du réseau en temps réel")
subparsers.add_parser("favorites", help="Ajouter, enlever des favories")
subparsers.add_parser("alerts", help="Lister les stations vides, presque vides, bref toute les alertes")
subparsers.add_parser("dashboard", help="Tableau de bord, mis à jour en temps réel")
subparsers.add_parser("collect", help="Enregistre l'état de toute les stations à intervalle régulier")
subparsers.add_parser("history", help="Affiche les périodes et relevés enregistrés")
subparsers.add_parser("query", help="Analyser l'historique enregistré")

args = parser.parse_args()
