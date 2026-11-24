import argparse
from projet.functions import station_list, station_search, refresh, velo_status, velo_alerts
from projet.functions import init_parser as initialisation

parser = argparse.ArgumentParser(description="Pour les vélos")
subparsers = parser.add_subparsers(dest="commande", required=True)


init_parser = subparsers.add_parser("init", help="Prépare l'outil")
init_parser.add_argument("--force", action="store_true", help="Force l'initialisation")


subparsers.add_parser("refresh", help="Met à jour les données")


station_parser = subparsers.add_parser("station", help="Consulter une station")
station_subparsers = station_parser.add_subparsers(dest="station_commande", required=True)
station_subparsers.add_parser("list", help="Liste toutes les stations")
search_parser = station_subparsers.add_parser("search", help="Recherche une station")
search_parser.add_argument("nom", help="Nom de la station à rechercher")


subparsers.add_parser("status", help="Résumé de l'état du réseau en temps réel")


favorite_parser = subparsers.add_parser("favorites", help="Gérer les favoris")
favorite_subparsers = favorite_parser.add_subparsers(dest="favorite_commande", required=True)
favorite_add = favorite_subparsers.add_parser("add", help="Ajouter un favori")
favorite_add.add_argument("station", type=str)
favorite_remove = favorite_subparsers.add_parser("remove", help="Enlever un favori")
favorite_remove.add_argument("station", type=str)


alert_parser = subparsers.add_parser("alerts", help="Lister les stations vides, presque vides, bref toute les alertes")
alert_parser.add_argument("--low-bikes", type=int)
alert_parser.add_argument("--low-docks", type=int)


dashboard_parser = subparsers.add_parser("dashboard", help="Tableau de bord, mis à jour en temps réel")
dashboard_parser.add_argument("--refresh", type=int)


collect_parser = subparsers.add_parser("collect", help="Enregistre l'état de toute les stations à intervalle régulier")
collect_parser.add_argument("--interval", type=int)
collect_parser.add_argument("--duration", type=int)
collect_parser.add_argument("--until", type=str)
collect_parser.add_argument("--once", action="store_true")


history_parser = subparsers.add_parser("history", help="Affiche les périodes et relevés enregistrés")
history_parser.add_argument("--from", type=str)
history_parser.add_argument("--to", type=str)


query_parser = subparsers.add_parser("query", help="Analyser l'historique du réseau")
query_parser.add_argument("--metric", nargs="+", required=True, choices=["avg_bikes", "avg_docks", "empty_rate", "full_rate"], help="Métrique(s) à analyser")
query_parser.add_argument("--date", type=str, help="Sélectionne un jour (AAAA-MM-JJ)")
query_parser.add_argument("--from", dest="date_from", type=str, help="Date et heure de début")
query_parser.add_argument("--to", dest="date_to", type=str, help="Date et heure de fin")
query_parser.add_argument("--period", nargs="+", type=int, help="Numéro(s) de période")
query_parser.add_argument("--days", nargs="+", help="Jour(s) de la semaine ou weekdays/weekend")
query_parser.add_argument("--hours", type=str, help="Plage horaire (ex: 7-9)")
query_parser.add_argument("--station", type=str, help="ID d'une station")
query_parser.add_argument("--by", choices=["station", "hour", "weekday", "day"], help="Regroupe les résultats")
query_parser.add_argument("--top", type=int, help="Limite le nombre de résultats affichés")

args = parser.parse_args()
if args.commande == "station":

    if args.station_commande == "list":
        station_list()

    elif args.station_commande == "search":
        station_search(args.nom)
elif args.commande == "refresh":
    refresh()
elif args.commande == "status":
    velo_status()
elif args.commande == "init":
    initialisation()
elif args.commande == "alerts":
    velo_alerts()
